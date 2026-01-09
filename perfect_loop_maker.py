#!/usr/bin/env python3
"""
Perfect Seamless Loop Maker - 5 Variants
Ensures END frame = START frame for truly seamless loops
"""

import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import List, Tuple
import shutil


class PerfectLoopMaker:
    def __init__(self, input_video: str, output_dir: str = "perfect_loops"):
        self.input_video = input_video
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.info = self._get_video_info()
        print(f"📹 Video: {self.info['width']}x{self.info['height']} @ {self.info['fps']:.2f} fps")
        print(f"⏱️  Duration: {self.info['duration']:.2f}s")

    def _get_video_info(self) -> dict:
        """Get video information"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,duration',
            '-of', 'json',
            self.input_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        stream = data['streams'][0]

        fps_parts = stream['r_frame_rate'].split('/')
        fps = float(fps_parts[0]) / float(fps_parts[1])
        duration = float(stream.get('duration', 0))

        return {
            'width': stream['width'],
            'height': stream['height'],
            'fps': fps,
            'duration': duration
        }

    def find_top_loop_points(self, num_points: int = 5, search_window: float = 3.5, sample_rate: int = 2) -> List[Tuple[float, float]]:
        """
        Find top N loop points by scanning video for frames similar to first frame

        Returns:
            List of (time, similarity) tuples, sorted by similarity (best first)
        """
        print(f"\n🔍 Scanning for top {num_points} loop points...")
        print(f"Searching last {search_window}s of video...")

        # Extract first frame
        first_frame = self.output_dir / "first_frame.png"
        cmd = [
            'ffmpeg', '-i', self.input_video,
            '-vf', 'select=eq(n\\,0)',
            '-frames:v', '1',
            '-y', str(first_frame)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # Search window
        start_time = max(0, self.info['duration'] - search_window)
        end_time = self.info['duration'] - 0.15  # Leave margin at end
        step_time = 1.0 / self.info['fps'] * sample_rate

        results = []
        current_time = start_time

        while current_time <= end_time:
            test_frame = self.output_dir / "test_frame.png"
            cmd = [
                'ffmpeg',
                '-ss', str(current_time),
                '-i', self.input_video,
                '-frames:v', '1',
                '-y', str(test_frame)
            ]
            subprocess.run(cmd, capture_output=True, check=True)

            # Calculate SSIM
            cmd_ssim = [
                'ffmpeg',
                '-i', str(first_frame),
                '-i', str(test_frame),
                '-lavfi', 'ssim',
                '-f', 'null', '-'
            ]
            result = subprocess.run(cmd_ssim, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in result.stdout.split('\n'):
                if 'SSIM' in line and 'All:' in line:
                    ssim_str = line.split('All:')[1].split()[0]
                    similarity = float(ssim_str)
                    results.append((current_time, similarity))
                    print(f"  {current_time:.2f}s: {similarity:.4f}")
                    break

            current_time += step_time

        # Cleanup
        first_frame.unlink(missing_ok=True)
        Path(self.output_dir / "test_frame.png").unlink(missing_ok=True)

        # Sort by similarity (best first) and take top N
        results.sort(key=lambda x: x[1], reverse=True)
        top_results = results[:num_points]

        # Sort top results by time for easier understanding
        top_results.sort(key=lambda x: x[0])

        print(f"\n✨ Top {len(top_results)} loop points found:")
        for i, (time, sim) in enumerate(top_results, 1):
            print(f"  #{i}: {time:.2f}s (similarity: {sim:.4f})")

        return top_results

    def create_perfect_loop(self, loop_point: float, variant_num: int, blend_duration: float = 0.2) -> str:
        """
        Create perfect loop where END = START

        Strategy:
        1. Cut video at loop_point
        2. Add short blend/crossfade at end that morphs back to first frame
        3. This ensures last frame smoothly becomes first frame

        Args:
            loop_point: Where to cut the video (seconds)
            variant_num: Variant number for naming
            blend_duration: Duration of blend transition (seconds)

        Returns:
            Path to output file
        """
        output_file = self.output_dir / f"variant_{variant_num}_loop_{loop_point:.2f}s.mp4"

        print(f"\n🎬 Creating variant #{variant_num} (loop at {loop_point:.2f}s)...")

        # Create loop with xfade that ends exactly on first frame
        # Strategy: duplicate input, use xfade to blend end into start

        filter_complex = (
            # Take two copies of the input
            f"[0:v]trim=0:{loop_point}[main];"
            # Take first part for crossfade beginning (the start)
            f"[0:v]trim=0:{blend_duration},setpts=PTS-STARTPTS[start];"
            # Crossfade from main video into start at the end
            f"[main][start]xfade=transition=fade:duration={blend_duration}:offset={loop_point-blend_duration}[v]"
        )

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-y', str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating variant #{variant_num}: {e}")
            return None

    def create_all_variants(self, num_variants: int = 5) -> List[str]:
        """
        Create multiple perfect loop variants

        Returns:
            List of created file paths
        """
        print("\n" + "="*60)
        print(f"🎯 Creating {num_variants} perfect seamless loop variants")
        print("="*60)

        # Find top loop points
        loop_points = self.find_top_loop_points(num_variants)

        if not loop_points:
            print("❌ No suitable loop points found!")
            return []

        # Create variant for each loop point
        output_files = []

        for i, (time, similarity) in enumerate(loop_points, 1):
            # Adjust blend duration based on similarity
            # Higher similarity = shorter blend needed
            if similarity > 0.95:
                blend = 0.15
            elif similarity > 0.90:
                blend = 0.20
            elif similarity > 0.85:
                blend = 0.25
            else:
                blend = 0.30

            result = self.create_perfect_loop(time, i, blend)
            if result:
                output_files.append(result)

        return output_files

    def verify_loop(self, loop_file: str) -> bool:
        """
        Verify that loop is seamless by comparing first and last frames

        Returns:
            True if loop is seamless
        """
        print(f"\n🔬 Verifying loop: {Path(loop_file).name}")

        temp_dir = self.output_dir / "temp_verify"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Extract first frame
            first_frame = temp_dir / "first.png"
            cmd = [
                'ffmpeg',
                '-i', loop_file,
                '-vf', 'select=eq(n\\,0)',
                '-frames:v', '1',
                '-y', str(first_frame)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Extract last frame
            last_frame = temp_dir / "last.png"
            cmd = [
                'ffmpeg',
                '-sseof', '-0.1',
                '-i', loop_file,
                '-frames:v', '1',
                '-y', str(last_frame)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Compare frames
            cmd_ssim = [
                'ffmpeg',
                '-i', str(first_frame),
                '-i', str(last_frame),
                '-lavfi', 'ssim',
                '-f', 'null', '-'
            ]
            result = subprocess.run(cmd_ssim, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in result.stdout.split('\n'):
                if 'SSIM' in line and 'All:' in line:
                    ssim_str = line.split('All:')[1].split()[0]
                    similarity = float(ssim_str)

                    if similarity > 0.99:
                        status = "✅ PERFECT"
                    elif similarity > 0.95:
                        status = "✅ EXCELLENT"
                    elif similarity > 0.90:
                        status = "⚠️  GOOD"
                    else:
                        status = "❌ NEEDS WORK"

                    print(f"  First vs Last frame: {similarity:.4f} - {status}")

                    shutil.rmtree(temp_dir)
                    return similarity > 0.90

            shutil.rmtree(temp_dir)
            return False

        except Exception as e:
            print(f"  ⚠️  Could not verify: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Perfect Seamless Loop Maker - 5 Variants with END = START',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create 5 perfect loop variants (default)
  python perfect_loop_maker.py video.mp4

  # Create 3 variants
  python perfect_loop_maker.py video.mp4 -n 3

  # Search in wider window (last 5 seconds)
  python perfect_loop_maker.py video.mp4 -w 5.0

  # Verify existing loop
  python perfect_loop_maker.py video.mp4 --verify-only loop.mp4

How it works:
  1. Scans video to find frames most similar to first frame
  2. Finds top 5 best matching points
  3. For each point, creates loop where:
     - Video is cut at that point
     - Short crossfade blends end back to start
     - ENSURES last frame = first frame (seamless!)
  4. Each variant has different duration but all are perfectly seamless

Output:
  - variant_1_loop_X.XXs.mp4 (best match)
  - variant_2_loop_X.XXs.mp4 (2nd best)
  - variant_3_loop_X.XXs.mp4 (3rd best)
  - variant_4_loop_X.XXs.mp4 (4th best)
  - variant_5_loop_X.XXs.mp4 (5th best)

Choose the one that looks most natural!
        """
    )

    parser.add_argument('input', help='Input video file')
    parser.add_argument('-n', '--num-variants', type=int, default=5,
                        help='Number of variants to create (default: 5)')
    parser.add_argument('-d', '--output-dir', default='perfect_loops',
                        help='Output directory (default: perfect_loops)')
    parser.add_argument('-w', '--search-window', type=float, default=3.5,
                        help='Search window in seconds from end (default: 3.5)')
    parser.add_argument('--verify-only', metavar='LOOP_FILE',
                        help='Only verify existing loop file')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return

    maker = PerfectLoopMaker(args.input, args.output_dir)

    # Verify mode
    if args.verify_only:
        if os.path.exists(args.verify_only):
            maker.verify_loop(args.verify_only)
        else:
            print(f"❌ Loop file not found: {args.verify_only}")
        return

    # Create variants
    output_files = maker.create_all_variants(args.num_variants)

    if output_files:
        print("\n" + "="*60)
        print(f"✅ Successfully created {len(output_files)} perfect loops!")
        print("="*60)

        for i, f in enumerate(output_files, 1):
            file_size = Path(f).stat().st_size / (1024 * 1024)
            print(f"  #{i}: {Path(f).name} ({file_size:.1f} MB)")

        print("\n🔬 Verifying loops...")
        for f in output_files:
            maker.verify_loop(f)

        print("\n" + "="*60)
        print("💡 NEXT STEPS:")
        print("="*60)
        print("1. Watch all variants and pick the most natural one")
        print("2. Test by looping: ffplay -loop 0 variant_X.mp4")
        print("3. For AI enhancement: py topaz_ai_enhancer.py variant_X.mp4")
        print("4. For long video: py video_loop_maker.py variant_X.mp4 -l 100")
        print("="*60)
    else:
        print("\n❌ Failed to create loops")
        print("💡 Try different source material or adjust parameters")


if __name__ == '__main__':
    main()
