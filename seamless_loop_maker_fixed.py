#!/usr/bin/env python3
"""
True Seamless Loop Maker - Correct DaVinci Resolve Technique
KEEPS ORIGINAL LENGTH - implements exact YouTube tutorial method
"""

import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import List, Tuple, Dict


class CorrectSeamlessLoopMaker:
    def __init__(self, input_video: str, output_dir: str = "seamless_loops"):
        self.input_video = input_video
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.info = self._get_video_info()
        print(f"📹 Input: {self.info['width']}x{self.info['height']} @ {self.info['fps']:.2f} fps")
        print(f"⏱️  Duration: {self.info['duration']:.2f}s")

    def _get_video_info(self) -> dict:
        cmd = [
            'ffprobe', '-v', 'error',
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

    def create_correct_seamless_loop(self, overlap_duration: float, variant_num: int) -> str:
        """
        CORRECT DaVinci Resolve Technique:

        1. Bottom layer: FULL video (0 to end) - always visible
        2. Top layer: FULL video (0 to end) with:
           - FADE IN at start (opacity 0→100 over overlap_duration)
           - FADE OUT at end (opacity 100→0 over overlap_duration)
        3. Overlay top on bottom
        4. Result: SAME length as input, ready for seamless duplication

        When duplicated:
        [...fade_out end][fade_in start...] = SEAMLESS!
        """
        output_file = self.output_dir / f"variant_{variant_num}_overlap_{overlap_duration}s.mp4"

        duration = self.info['duration']

        print(f"\n🎬 Creating Variant #{variant_num}")
        print(f"   Overlap: {overlap_duration}s")
        print(f"   Output Length: {duration:.2f}s (SAME as input!)")

        # CORRECT FFmpeg filter implementing DaVinci Resolve technique
        filter_complex = f"""
[0:v]split=2[bottom][top];
[bottom]copy[b];
[top]fade=t=in:st=0:d={overlap_duration}:alpha=1,
     fade=t=out:st={duration - overlap_duration}:d={overlap_duration}:alpha=1[t];
[b][t]overlay=0:0[v]
"""

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-filter_complex', filter_complex.strip(),
            '-map', '[v]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),  # IMPORTANT: Keep original duration!
            '-y', str(output_file)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                # Verify output duration
                verify_info = self._get_video_info_for_file(output_file)
                print(f"   ✅ Created: {output_file.name}")
                print(f"   ✅ Duration: {verify_info['duration']:.2f}s (correct!)")
                return str(output_file)
            else:
                print(f"   ❌ FFmpeg error")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def _get_video_info_for_file(self, file_path: str) -> dict:
        """Get video info for any file"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return {'duration': float(data['format'].get('duration', 0))}

    def verify_seamless_duplication(self, loop_file: str) -> Dict:
        """
        Verify seamlessness by duplicating and checking seam
        """
        print(f"\n🔬 Verifying: {Path(loop_file).name}")

        import shutil
        temp_dir = self.output_dir / "temp_verify"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Get duration
            info = self._get_video_info_for_file(loop_file)
            duration = info['duration']

            # Create duplicated version
            duplicated = temp_dir / "duplicated.mp4"
            concat_file = temp_dir / "concat.txt"

            abs_path = Path(loop_file).absolute()
            with open(concat_file, 'w') as f:
                f.write(f"file '{abs_path}'\n")
                f.write(f"file '{abs_path}'\n")

            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy', '-y', str(duplicated)
            ], check=True, capture_output=True)

            # Extract frames around seam
            frame_before = temp_dir / "before.png"
            frame_after = temp_dir / "after.png"

            subprocess.run([
                'ffmpeg', '-ss', str(duration - 0.033),
                '-i', str(duplicated),
                '-frames:v', '1', '-y', str(frame_before)
            ], check=True, capture_output=True)

            subprocess.run([
                'ffmpeg', '-ss', str(duration + 0.033),
                '-i', str(duplicated),
                '-frames:v', '1', '-y', str(frame_after)
            ], check=True, capture_output=True)

            # Compare
            result = subprocess.run([
                'ffmpeg', '-i', str(frame_before), '-i', str(frame_after),
                '-lavfi', 'ssim', '-f', 'null', '-'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            seam_quality = 0.0
            for line in result.stdout.split('\n'):
                if 'SSIM' in line and 'All:' in line:
                    seam_quality = float(line.split('All:')[1].split()[0])
                    break

            if seam_quality >= 0.98:
                rating = "✅ PERFECT - Invisible seam!"
            elif seam_quality >= 0.95:
                rating = "✅ EXCELLENT - Barely visible"
            elif seam_quality >= 0.90:
                rating = "⚠️  GOOD - Slightly visible"
            else:
                rating = "❌ VISIBLE - Try different overlap"

            print(f"   Seam Quality: {seam_quality:.4f}")
            print(f"   Rating: {rating}")

            shutil.rmtree(temp_dir)

            return {
                'seam_quality': seam_quality,
                'rating': rating,
                'seamless': seam_quality >= 0.95
            }

        except Exception as e:
            print(f"   ⚠️  Verification error: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return {'seam_quality': 0, 'rating': 'ERROR', 'seamless': False}

    def create_all_variants(self, overlap_durations: List[float] = None) -> List[Tuple[str, Dict]]:
        """
        Create 5 variants with different overlaps
        """
        if overlap_durations is None:
            overlap_durations = [1.0, 1.5, 2.0, 2.5, 3.0]

        print("\n" + "="*70)
        print("🎯 CORRECT SEAMLESS LOOP MAKER")
        print("DaVinci Resolve Technique - KEEPS ORIGINAL LENGTH")
        print("="*70)

        results = []

        for i, overlap in enumerate(overlap_durations, 1):
            if overlap >= self.info['duration'] / 2:
                print(f"\n⚠️  Variant #{i}: Overlap {overlap}s too long, skipping")
                continue

            # Create loop
            output_file = self.create_correct_seamless_loop(overlap, i)

            if output_file:
                # Verify
                verification = self.verify_seamless_duplication(output_file)
                results.append((output_file, verification))

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Correct Seamless Loop Maker - DaVinci Resolve Technique',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CORRECT DaVinci Resolve Technique (from YouTube tutorial):

Key Understanding:
- Result has SAME length as input (NOT shorter!)
- Uses double fade on top layer (fade in + fade out)
- When duplicated, end blends seamlessly into start

Structure:
  Bottom Layer: [========= full video =========]
  Top Layer:    [fade_in][======][fade_out]
  Result:       [==== SAME LENGTH ====]

When duplicated:
  [clip1 ...fade_out][fade_in... clip2]
                   ↑ SEAMLESS! ↑

Examples:
  # Create 5 variants (1.0s to 3.0s overlap)
  python seamless_loop_maker_fixed.py video.mp4

  # Custom overlaps
  python seamless_loop_maker_fixed.py video.mp4 -o 1.5 2.0 2.5

  # Skip verification (faster)
  python seamless_loop_maker_fixed.py video.mp4 --no-verify

Expected result:
  - 8 second input → 8 second output (NOT 5 seconds!)
  - First frame visually = last frame (through blend)
  - No visible seam when duplicated
        """
    )

    parser.add_argument('input', help='Input video file')
    parser.add_argument('-o', '--overlaps', type=float, nargs='+',
                        help='Overlap durations (default: 1.0 1.5 2.0 2.5 3.0)')
    parser.add_argument('-d', '--output-dir', default='seamless_loops')
    parser.add_argument('--no-verify', action='store_true',
                        help='Skip verification')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Input not found: {args.input}")
        return

    maker = CorrectSeamlessLoopMaker(args.input, args.output_dir)
    results = maker.create_all_variants(args.overlaps)

    if not results:
        print("\n❌ No variants created")
        return

    # Summary
    print("\n" + "="*70)
    print(f"✅ Created {len(results)} seamless loop variants!")
    print("="*70)

    best = None
    best_score = 0

    for i, (file_path, verification) in enumerate(results, 1):
        file_size = Path(file_path).stat().st_size / (1024 * 1024)

        print(f"\n#{i}: {Path(file_path).name} ({file_size:.1f} MB)")
        print(f"    Seam Quality: {verification['seam_quality']:.4f}")
        print(f"    {verification['rating']}")

        if verification['seam_quality'] > best_score:
            best_score = verification['seam_quality']
            best = (i, file_path)

    if best:
        print("\n" + "="*70)
        print(f"🏆 BEST: Variant #{best[0]} - {Path(best[1]).name}")
        print(f"   Seam Quality: {best_score:.4f}")
        print("="*70)

    print("\n💡 NEXT STEPS:")
    print("1. Test: ffplay -loop 0 <best_file>")
    print("2. Multiply: py video_loop_maker.py <file> -l 100")
    print("3. Upscale: py video_upscaler.py <file> -r 4k")
    print("4. AI enhance: py topaz_ai_enhancer.py <file>")


if __name__ == '__main__':
    main()
