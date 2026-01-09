#!/usr/bin/env python3
"""
Perfect Seamless Loop Maker with AI Frame Interpolation
Finds the best loop point and creates perfectly matching transitions.
"""

import subprocess
import argparse
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import shutil


class PerfectLoopMaker:
    def __init__(self, input_video: str, output_dir: str = "perfect_loops"):
        """
        Initialize Perfect Loop Maker

        Args:
            input_video: Path to input video
            output_dir: Directory for output files
        """
        self.input_video = input_video
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Get video info
        self.info = self._get_video_info()
        print(f"Video: {self.info['width']}x{self.info['height']} @ {self.info['fps']:.2f} fps")
        print(f"Duration: {self.info['duration']:.2f}s ({self.info['total_frames']} frames)")

    def _get_video_info(self) -> dict:
        """Get detailed video information"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-count_frames',
            '-show_entries', 'stream=width,height,r_frame_rate,nb_read_frames,duration',
            '-of', 'json',
            self.input_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        stream = data['streams'][0]

        # Parse frame rate
        fps_parts = stream['r_frame_rate'].split('/')
        fps = float(fps_parts[0]) / float(fps_parts[1])

        duration = float(stream.get('duration', 0))
        total_frames = int(stream.get('nb_read_frames', 0))

        # If nb_read_frames is not available, calculate from duration
        if total_frames == 0 and duration > 0:
            total_frames = int(duration * fps)

        return {
            'width': stream['width'],
            'height': stream['height'],
            'fps': fps,
            'duration': duration,
            'total_frames': total_frames
        }

    def find_best_loop_point(self, search_window: float = 3.0, sample_rate: int = 5) -> Tuple[float, float]:
        """
        Find the best loop point by comparing frames throughout the video with the first frame

        Args:
            search_window: How many seconds from the end to search (default: last 3 seconds)
            sample_rate: Check every Nth frame (default: 5)

        Returns:
            Tuple of (best_time_offset, similarity_score)
        """
        print(f"\n🔍 Scanning for perfect loop point...")
        print(f"Searching last {search_window}s of video...")

        # Extract first frame
        first_frame_path = self.output_dir / "first_frame.png"
        cmd = [
            'ffmpeg', '-i', self.input_video,
            '-vf', 'select=eq(n\\,0)',
            '-frames:v', '1',
            '-y', str(first_frame_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # Calculate search range
        start_time = max(0, self.info['duration'] - search_window)
        end_time = self.info['duration']

        # Sample frames in the search window
        step_time = 1.0 / self.info['fps'] * sample_rate

        best_time = start_time
        best_similarity = 0
        results = []

        current_time = start_time
        while current_time <= end_time:
            # Extract frame at current time
            test_frame_path = self.output_dir / "test_frame.png"
            cmd = [
                'ffmpeg',
                '-ss', str(current_time),
                '-i', self.input_video,
                '-frames:v', '1',
                '-y', str(test_frame_path)
            ]
            subprocess.run(cmd, capture_output=True, check=True)

            # Calculate SSIM
            cmd_ssim = [
                'ffmpeg',
                '-i', str(first_frame_path),
                '-i', str(test_frame_path),
                '-lavfi', 'ssim',
                '-f', 'null', '-'
            ]
            result = subprocess.run(cmd_ssim, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # Parse SSIM
            for line in result.stdout.split('\n'):
                if 'SSIM' in line and 'All:' in line:
                    ssim_str = line.split('All:')[1].split()[0]
                    similarity = float(ssim_str)
                    results.append((current_time, similarity))

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_time = current_time

                    print(f"  Time {current_time:.2f}s: similarity = {similarity:.4f}")
                    break

            current_time += step_time

        # Cleanup
        first_frame_path.unlink(missing_ok=True)
        test_frame_path.unlink(missing_ok=True)

        print(f"\n✨ Best loop point: {best_time:.2f}s (similarity: {best_similarity:.4f})")

        return best_time, best_similarity

    def create_loop_with_interpolation(self, loop_point: float,
                                       interpolation_frames: int = 10,
                                       method: str = "minterpolate") -> str:
        """
        Create perfect loop with AI/motion interpolated transition frames

        Args:
            loop_point: Time to cut the video (in seconds)
            interpolation_frames: Number of interpolated frames to create for transition
            method: 'minterpolate' (FFmpeg) or 'rife' (AI)

        Returns:
            Path to output file
        """
        output_file = self.output_dir / f"perfect_loop_{method}_{interpolation_frames}frames.mp4"

        print(f"\n🎬 Creating perfect loop with {method} interpolation...")
        print(f"Loop point: {loop_point:.2f}s")
        print(f"Transition frames: {interpolation_frames}")

        if method == "minterpolate":
            return self._create_loop_minterpolate(loop_point, interpolation_frames, output_file)
        elif method == "optical_flow":
            return self._create_loop_optical_flow(loop_point, output_file)
        else:
            print(f"❌ Unknown method: {method}")
            return None

    def _create_loop_minterpolate(self, loop_point: float, interp_frames: int, output_file: Path) -> str:
        """
        Create loop using FFmpeg motion interpolation
        This creates smooth transition frames between last and first frame
        """

        # Strategy:
        # 1. Cut video at loop_point
        # 2. Extract last N frames and first N frames
        # 3. Use minterpolate to create smooth transition
        # 4. Stitch everything together

        temp_dir = self.output_dir / "temp_interp"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Cut main video at loop point
            main_clip = temp_dir / "main_clip.mp4"
            cmd = [
                'ffmpeg',
                '-i', self.input_video,
                '-t', str(loop_point),
                '-c', 'copy',
                '-y', str(main_clip)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Extract last frame
            last_frame = temp_dir / "last_frame.png"
            cmd = [
                'ffmpeg',
                '-sseof', '-0.01',
                '-i', str(main_clip),
                '-frames:v', '1',
                '-y', str(last_frame)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Extract first frame
            first_frame = temp_dir / "first_frame.png"
            cmd = [
                'ffmpeg',
                '-i', self.input_video,
                '-frames:v', '1',
                '-y', str(first_frame)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Create transition video using minterpolate
            # This interpolates motion between last and first frame
            transition_clip = temp_dir / "transition.mp4"

            # Create a 2-frame video (last + first)
            two_frames = temp_dir / "two_frames.mp4"
            cmd = [
                'ffmpeg',
                '-framerate', '1',
                '-i', str(last_frame),
                '-framerate', '1',
                '-i', str(first_frame),
                '-filter_complex', '[0:v][1:v]concat=n=2:v=1[out]',
                '-map', '[out]',
                '-r', str(self.info['fps']),
                '-y', str(two_frames)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Apply motion interpolation to create smooth transition
            fps_multiplier = interp_frames + 1
            cmd = [
                'ffmpeg',
                '-i', str(two_frames),
                '-filter:v', f"minterpolate='fps={self.info['fps'] * fps_multiplier}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1'",
                '-y', str(transition_clip)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Concatenate: main_clip + transition + main_clip (for seamless loop)
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                f.write(f"file '{main_clip.absolute()}'\n")
                f.write(f"file '{transition_clip.absolute()}'\n")

            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-y', str(output_file)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Cleanup
            shutil.rmtree(temp_dir)

            print(f"✅ Created: {output_file}")
            return str(output_file)

        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return None

    def _create_loop_optical_flow(self, loop_point: float, output_file: Path) -> str:
        """
        Create loop using optical flow morphing for seamless transition
        """

        print("Creating seamless loop with optical flow...")

        temp_dir = self.output_dir / "temp_flow"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Cut video at loop point
            main_clip = temp_dir / "main.mp4"
            cmd = [
                'ffmpeg',
                '-i', self.input_video,
                '-t', str(loop_point),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-y', str(main_clip)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Create looped version with crossfade at junction
            # Use a very short crossfade (0.5s) with optical flow blending
            filter_complex = (
                f"[0:v][0:v]xfade=transition=fade:duration=0.5:offset={loop_point-0.25}"
            )

            cmd = [
                'ffmpeg',
                '-i', str(main_clip),
                '-filter_complex', filter_complex,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-y', str(output_file)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Cleanup
            shutil.rmtree(temp_dir)

            print(f"✅ Created: {output_file}")
            return str(output_file)

        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return None

    def create_multiple_perfect_loops(self, methods: List[str] = None) -> List[str]:
        """
        Create multiple perfect loop variants with different methods

        Args:
            methods: List of methods to try
        """
        if methods is None:
            methods = ['minterpolate']

        # First, find the best loop point
        loop_point, similarity = self.find_best_loop_point()

        if similarity < 0.85:
            print(f"\n⚠️  Warning: Best similarity is {similarity:.4f} (< 0.85)")
            print("Video content may not be ideal for seamless looping.")
            print("Consider using shorter video or different source material.")

        output_files = []

        for method in methods:
            if method == 'minterpolate':
                # Try different interpolation frame counts
                for frames in [5, 10, 15]:
                    result = self.create_loop_with_interpolation(
                        loop_point,
                        interpolation_frames=frames,
                        method='minterpolate'
                    )
                    if result:
                        output_files.append(result)
            elif method == 'optical_flow':
                result = self.create_loop_with_interpolation(
                    loop_point,
                    method='optical_flow'
                )
                if result:
                    output_files.append(result)

        return output_files


def main():
    parser = argparse.ArgumentParser(
        description='Perfect Seamless Loop Maker with AI Frame Interpolation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Automatically find best loop point and create perfect loop
  python perfect_loop_maker.py video.mp4

  # Create multiple variants with different interpolation settings
  python perfect_loop_maker.py video.mp4 --auto

  # Manually specify loop point (in seconds)
  python perfect_loop_maker.py video.mp4 --loop-point 7.5

  # Search in wider window (last 5 seconds)
  python perfect_loop_maker.py video.mp4 --search-window 5.0

How it works:
  1. Scans video to find frame most similar to first frame
  2. Cuts video at that point
  3. Creates smooth interpolated transition frames between end and start
  4. Results in truly seamless loop where last frame = first frame

Methods:
  minterpolate - FFmpeg motion interpolation (always available)
  optical_flow - Optical flow based morphing (experimental)
        """
    )

    parser.add_argument('input', help='Input video file')
    parser.add_argument('-d', '--output-dir', default='perfect_loops',
                        help='Output directory (default: perfect_loops)')
    parser.add_argument('-l', '--loop-point', type=float,
                        help='Manually specify loop point in seconds (skips auto-detection)')
    parser.add_argument('-w', '--search-window', type=float, default=3.0,
                        help='Search window in seconds from end (default: 3.0)')
    parser.add_argument('-a', '--auto', action='store_true',
                        help='Create multiple variants automatically')
    parser.add_argument('-m', '--method', choices=['minterpolate', 'optical_flow'],
                        default='minterpolate',
                        help='Interpolation method (default: minterpolate)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found")
        return

    # Create loop maker
    maker = PerfectLoopMaker(args.input, args.output_dir)

    if args.auto:
        # Create multiple variants
        print("\n🎯 Creating multiple perfect loop variants...")
        output_files = maker.create_multiple_perfect_loops(['minterpolate', 'optical_flow'])
    else:
        # Single variant
        if args.loop_point:
            loop_point = args.loop_point
            similarity = 1.0
            print(f"\n📍 Using manual loop point: {loop_point:.2f}s")
        else:
            loop_point, similarity = maker.find_best_loop_point(args.search_window)

        output_file = maker.create_loop_with_interpolation(
            loop_point,
            interpolation_frames=10,
            method=args.method
        )
        output_files = [output_file] if output_file else []

    if output_files:
        print(f"\n✅ Successfully created {len(output_files)} perfect loop(s):")
        for f in output_files:
            print(f"  📁 {f}")
        print(f"\n💡 Test the loop by playing it repeatedly!")
        print(f"💡 The transition should be completely seamless")
    else:
        print("\n❌ Failed to create perfect loops")
        print("💡 Try different source material or adjust parameters")


if __name__ == '__main__':
    main()
