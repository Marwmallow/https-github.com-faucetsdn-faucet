#!/usr/bin/env python3
"""
Seamless Video Loop Maker
Creates multiple variants of seamlessly looped videos with different crossfade durations.
"""

import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import List, Tuple


class VideoLooper:
    def __init__(self, input_video: str, output_dir: str = "output", loop_count: int = 3):
        """
        Initialize VideoLooper

        Args:
            input_video: Path to input video file
            output_dir: Directory for output files
            loop_count: Number of times to repeat the loop in final video
        """
        self.input_video = input_video
        self.output_dir = Path(output_dir)
        self.loop_count = loop_count
        self.output_dir.mkdir(exist_ok=True)

        # Get video duration
        self.duration = self._get_video_duration()
        print(f"Video duration: {self.duration:.2f} seconds")

    def _get_video_duration(self) -> float:
        """Get video duration using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            self.input_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])

    def create_loop_variant(self, overlap_duration: float, variant_name: str) -> str:
        """
        Create a seamless loop with specified overlap duration

        Args:
            overlap_duration: Duration of crossfade in seconds
            variant_name: Name for this variant

        Returns:
            Path to output file
        """
        output_file = self.output_dir / f"{variant_name}_overlap_{overlap_duration}s.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (overlap: {overlap_duration}s)")

        # Calculate offset for the second clip
        offset = self.duration - overlap_duration

        if offset <= 0:
            print(f"❌ Error: Overlap {overlap_duration}s is too long for video duration {self.duration}s")
            return None

        # FFmpeg command to create seamless loop with crossfade
        # Strategy:
        # 1. Take full video as base
        # 2. Overlay the same video starting at (duration - overlap)
        # 3. Apply crossfade between them
        # 4. Repeat the resulting loop

        filter_complex = (
            # Split input into two streams
            f"[0:v]split=2[v1][v2];"
            # Trim second stream to start from the beginning (for looping back)
            f"[v2]trim=duration={overlap_duration},setpts=PTS-STARTPTS[v2trimmed];"
            # Trim first stream to full length
            f"[v1]trim=duration={self.duration}[v1full];"
            # Apply crossfade at the overlap point
            f"[v1full][v2trimmed]xfade=transition=fade:duration={overlap_duration}:offset={offset}[loop];"
            # Repeat the loop
            f"[loop]loop={self.loop_count-1}:size=1[outv]"
        )

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '0:a?',  # Copy audio if exists
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            '-y',  # Overwrite output file
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg error: {e.stderr.decode()}")
            return None

    def create_simple_loop(self, overlap_duration: float, variant_name: str) -> str:
        """
        Create a simpler seamless loop using concat and crossfade
        This method is more reliable for most cases

        Args:
            overlap_duration: Duration of crossfade in seconds
            variant_name: Name for this variant

        Returns:
            Path to output file
        """
        output_file = self.output_dir / f"{variant_name}_overlap_{overlap_duration}s.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (overlap: {overlap_duration}s)")

        # Calculate the offset point where crossfade starts
        offset = self.duration - overlap_duration

        if offset <= 0:
            print(f"❌ Error: Overlap {overlap_duration}s is too long for video duration {self.duration}s")
            return None

        # Create a seamless single loop using xfade
        # Then tile/loop it multiple times
        filter_complex = (
            f"[0:v][0:v]xfade=transition=fade:duration={overlap_duration}:offset={offset},"
            f"loop={self.loop_count}:size=1[outv]"
        )

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-y',
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg error: {e.stderr.decode()}")
            return None

    def create_multiple_variants(self, overlap_durations: List[float] = None) -> List[str]:
        """
        Create multiple loop variants with different overlap durations

        Args:
            overlap_durations: List of overlap durations to try (in seconds)

        Returns:
            List of paths to created video files
        """
        if overlap_durations is None:
            # Default: create variants from 0.5s to 3.0s
            overlap_durations = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

        # Filter out overlaps that are too long
        valid_overlaps = [o for o in overlap_durations if o < self.duration]

        if not valid_overlaps:
            print(f"❌ No valid overlap durations for video length {self.duration}s")
            return []

        print(f"\n🎯 Creating {len(valid_overlaps)} variants with overlaps: {valid_overlaps}")

        output_files = []
        for i, overlap in enumerate(valid_overlaps, 1):
            variant_name = f"variant_{i}"
            output_file = self.create_simple_loop(overlap, variant_name)
            if output_file:
                output_files.append(output_file)

        return output_files

    def analyze_frame_similarity(self, num_samples: int = 5) -> List[Tuple[float, float]]:
        """
        Analyze similarity between start and end frames at different offsets
        Returns list of (offset, similarity_score) tuples

        Args:
            num_samples: Number of different offsets to test

        Returns:
            List of (offset_seconds, similarity_score) tuples, sorted by similarity
        """
        print("\n🔍 Analyzing frame similarity for optimal loop point...")

        # Sample different offsets from 0.5s to 3.5s
        test_offsets = [0.5 + i * (3.0 / num_samples) for i in range(num_samples)]
        results = []

        for offset in test_offsets:
            if offset >= self.duration:
                continue

            # Extract first frame
            first_frame = self.output_dir / "temp_first.png"
            cmd_first = [
                'ffmpeg', '-i', self.input_video,
                '-vf', 'select=eq(n\\,0)',
                '-vframes', '1',
                '-y', str(first_frame)
            ]

            # Extract frame at offset from end
            frame_time = self.duration - offset
            end_frame = self.output_dir / "temp_end.png"
            cmd_end = [
                'ffmpeg', '-ss', str(frame_time),
                '-i', self.input_video,
                '-vframes', '1',
                '-y', str(end_frame)
            ]

            try:
                subprocess.run(cmd_first, check=True, capture_output=True, stderr=subprocess.DEVNULL)
                subprocess.run(cmd_end, check=True, capture_output=True, stderr=subprocess.DEVNULL)

                # Calculate similarity using FFmpeg's SSIM metric
                cmd_ssim = [
                    'ffmpeg',
                    '-i', str(first_frame),
                    '-i', str(end_frame),
                    '-lavfi', 'ssim',
                    '-f', 'null', '-'
                ]

                result = subprocess.run(cmd_ssim, capture_output=True, text=True, stderr=subprocess.STDOUT)

                # Parse SSIM from output
                for line in result.stdout.split('\n'):
                    if 'SSIM' in line and 'All:' in line:
                        # Extract SSIM value
                        ssim_str = line.split('All:')[1].split()[0]
                        similarity = float(ssim_str)
                        results.append((offset, similarity))
                        print(f"  Offset {offset:.2f}s: similarity = {similarity:.4f}")
                        break

                # Cleanup temp files
                first_frame.unlink(missing_ok=True)
                end_frame.unlink(missing_ok=True)

            except Exception as e:
                print(f"  ⚠️  Could not analyze offset {offset}s: {e}")
                continue

        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[1], reverse=True)

        if results:
            print(f"\n✨ Best overlap duration: {results[0][0]:.2f}s (similarity: {results[0][1]:.4f})")

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Create seamless video loops with multiple crossfade variants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create default variants (0.5s to 3.0s overlaps)
  python video_loop_maker.py input.mp4

  # Create custom overlaps
  python video_loop_maker.py input.mp4 -o 1.0 1.5 2.0 2.5

  # Analyze and create optimal variant
  python video_loop_maker.py input.mp4 --analyze

  # Specify output directory and loop count
  python video_loop_maker.py input.mp4 -d output_loops -l 5
        """
    )

    parser.add_argument('input', help='Input video file')
    parser.add_argument('-o', '--overlaps', type=float, nargs='+',
                        help='Overlap durations in seconds (default: 0.5 to 3.0)')
    parser.add_argument('-d', '--output-dir', default='output',
                        help='Output directory (default: output)')
    parser.add_argument('-l', '--loops', type=int, default=3,
                        help='Number of loop repetitions (default: 3)')
    parser.add_argument('-a', '--analyze', action='store_true',
                        help='Analyze frame similarity to find optimal overlap')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found")
        return

    # Create looper instance
    looper = VideoLooper(args.input, args.output_dir, args.loops)

    # Analyze if requested
    if args.analyze:
        similarities = looper.analyze_frame_similarity()
        if similarities:
            # Create variant with best overlap
            best_overlap = similarities[0][0]
            print(f"\n🎯 Creating optimized variant with {best_overlap:.2f}s overlap...")
            looper.create_simple_loop(best_overlap, "optimized")

            # Also create a few variants around the best one
            nearby_overlaps = [
                max(0.5, best_overlap - 0.5),
                best_overlap,
                min(looper.duration - 0.5, best_overlap + 0.5)
            ]
            nearby_overlaps = list(set(nearby_overlaps))  # Remove duplicates
            looper.create_multiple_variants(nearby_overlaps)
    else:
        # Create multiple variants
        output_files = looper.create_multiple_variants(args.overlaps)

        if output_files:
            print(f"\n✅ Successfully created {len(output_files)} variants:")
            for f in output_files:
                print(f"  📁 {f}")
            print(f"\n💡 Tip: Review all variants and choose the most seamless one!")
            print(f"💡 Use --analyze flag to automatically find the best overlap duration")


if __name__ == '__main__':
    main()
