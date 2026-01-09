#!/usr/bin/env python3
"""
Perfect Seamless Loop Maker (Fixed Version)
Finds best loop point and creates clean seamless loops
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
        print(f"Video: {self.info['width']}x{self.info['height']} @ {self.info['fps']:.2f} fps")
        print(f"Duration: {self.info['duration']:.2f}s")

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

    def find_best_loop_point(self, search_window: float = 3.0, sample_rate: int = 3) -> Tuple[float, float]:
        """
        Find best loop point by frame similarity

        Returns:
            (best_time, similarity_score)
        """
        print(f"\n🔍 Scanning for perfect loop point...")
        print(f"Searching last {search_window}s...")

        first_frame = self.output_dir / "first_frame.png"
        cmd = [
            'ffmpeg', '-i', self.input_video,
            '-vf', 'select=eq(n\\,0)',
            '-frames:v', '1',
            '-y', str(first_frame)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        start_time = max(0, self.info['duration'] - search_window)
        end_time = self.info['duration'] - 0.1  # Leave small margin
        step_time = 1.0 / self.info['fps'] * sample_rate

        best_time = start_time
        best_similarity = 0

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

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_time = current_time

                    print(f"  {current_time:.2f}s: {similarity:.4f}")
                    break

            current_time += step_time

        first_frame.unlink(missing_ok=True)
        Path(self.output_dir / "test_frame.png").unlink(missing_ok=True)

        print(f"\n✨ Best: {best_time:.2f}s (similarity: {best_similarity:.4f})")
        return best_time, best_similarity

    def create_simple_loop(self, loop_point: float, crossfade: float = 0.0) -> str:
        """
        Create simple loop by cutting at loop point

        Args:
            loop_point: Time to cut (seconds)
            crossfade: Optional crossfade duration (seconds)
        """
        if crossfade > 0:
            output_file = self.output_dir / f"loop_fade_{crossfade}s.mp4"
            print(f"\n🎬 Creating loop with {crossfade}s crossfade...")

            # Create loop with crossfade
            filter_complex = (
                f"[0:v][0:v]xfade=transition=fade:duration={crossfade}:"
                f"offset={loop_point - crossfade/2}"
            )

            cmd = [
                'ffmpeg',
                '-i', self.input_video,
                '-t', str(loop_point + crossfade/2),
                '-filter_complex', filter_complex,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-y', str(output_file)
            ]
        else:
            output_file = self.output_dir / f"loop_clean.mp4"
            print(f"\n🎬 Creating clean loop at {loop_point:.2f}s...")

            # Simple cut
            cmd = [
                'ffmpeg',
                '-i', self.input_video,
                '-t', str(loop_point),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y', str(output_file)
            ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            return None

    def create_multiple_variants(self) -> List[str]:
        """Create multiple loop variants"""
        # Find best loop point
        loop_point, similarity = self.find_best_loop_point()

        if similarity < 0.70:
            print(f"\n⚠️  Warning: Low similarity ({similarity:.4f})")
            print("Video may not be ideal for seamless looping")

        output_files = []

        # Clean cut at best point
        result = self.create_simple_loop(loop_point, crossfade=0)
        if result:
            output_files.append(result)

        # If similarity not perfect, also create crossfade variants
        if similarity < 0.90:
            print("\n💡 Creating crossfade variants for smoother transition...")
            for fade in [0.3, 0.5, 1.0]:
                result = self.create_simple_loop(loop_point, crossfade=fade)
                if result:
                    output_files.append(result)

        return output_files


def main():
    parser = argparse.ArgumentParser(
        description='Perfect Seamless Loop Maker (Fixed)',
        epilog="""
Examples:
  # Auto-find best loop point
  python perfect_loop_maker.py video.mp4

  # Create multiple variants
  python perfect_loop_maker.py video.mp4 --variants

  # Manual loop point
  python perfect_loop_maker.py video.mp4 --loop-point 7.5

  # Wider search window
  python perfect_loop_maker.py video.mp4 --search-window 5.0
        """
    )

    parser.add_argument('input', help='Input video')
    parser.add_argument('-d', '--output-dir', default='perfect_loops')
    parser.add_argument('-l', '--loop-point', type=float,
                        help='Manual loop point (seconds)')
    parser.add_argument('-w', '--search-window', type=float, default=3.0)
    parser.add_argument('-f', '--crossfade', type=float, default=0,
                        help='Crossfade duration (0 = none)')
    parser.add_argument('-v', '--variants', action='store_true',
                        help='Create multiple variants')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return

    maker = PerfectLoopMaker(args.input, args.output_dir)

    if args.variants:
        output_files = maker.create_multiple_variants()
    else:
        if args.loop_point:
            loop_point = args.loop_point
            print(f"\n📍 Using manual loop point: {loop_point:.2f}s")
        else:
            loop_point, _ = maker.find_best_loop_point(args.search_window)

        output_file = maker.create_simple_loop(loop_point, args.crossfade)
        output_files = [output_file] if output_file else []

    if output_files:
        print(f"\n✅ Created {len(output_files)} loop(s):")
        for f in output_files:
            print(f"  📁 {f}")
        print("\n💡 Test by playing on repeat!")
        print("💡 For AI enhancement, use topaz_ai_enhancer.py")
    else:
        print("\n❌ Failed to create loops")


if __name__ == '__main__':
    main()
