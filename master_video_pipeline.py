#!/usr/bin/env python3
"""
Master Video Pipeline - Complete Workflow
Loop → Multiply → Upscale → AI Enhance (Topaz)
"""

import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import List, Dict
import shutil


class MasterVideoPipeline:
    def __init__(self, input_video: str, output_dir: str = "master_output"):
        self.input_video = input_video
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.info = self._get_video_info()
        print(f"\n📹 Input: {self.info['width']}x{self.info['height']} @ {self.info['fps']:.2f} fps")
        print(f"⏱️  Duration: {self.info['duration']:.2f}s")

        # Find Topaz
        self.topaz_path = self._find_topaz()
        if self.topaz_path:
            print(f"✅ Topaz Video AI found: {self.topaz_path}")
        else:
            print("⚠️  Topaz Video AI not found (will use FFmpeg only)")

    def _get_video_info(self) -> dict:
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=width,height,r_frame_rate,duration',
               '-of', 'json', self.input_video]
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

    def _find_topaz(self) -> str:
        """Find Topaz Video AI installation"""
        paths = [
            'C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\tvai.exe',
            str(Path.home() / 'TopazVideoAIPortable' / 'Topaz Video AI.exe'),
            '/Applications/Topaz Video AI.app/Contents/MacOS/Topaz Video AI',
        ]
        for path in paths:
            if Path(path).exists():
                return path
        return None

    def step1_create_seamless_loop(self, overlap: float = 2.0) -> str:
        """Step 1: Create seamless loop using DaVinci technique"""
        print("\n" + "="*70)
        print("STEP 1: Creating Seamless Loop")
        print("="*70)

        output_file = self.output_dir / f"step1_loop_{overlap}s.mp4"

        duration = self.info['duration']
        loop_duration = duration - overlap

        # DaVinci Resolve technique
        filter_complex = f"""
[0:v]split=3[bottom][top1][top2];
[bottom]trim=0:{loop_duration},setpts=PTS-STARTPTS[bottom_layer];
[top1]trim=0:{overlap},setpts=PTS-STARTPTS,fade=t=out:st=0:d={overlap}:alpha=1[fade_out];
[top2]trim={duration - overlap}:{duration},setpts=PTS-STARTPTS,fade=t=in:st=0:d={overlap}:alpha=1,setpts=PTS+{loop_duration - overlap}/TB[fade_in];
[bottom_layer][fade_out]overlay=0:0[with_start];
[with_start][fade_in]overlay=0:0[v]
"""

        cmd = ['ffmpeg', '-i', self.input_video,
               '-filter_complex', filter_complex.strip(),
               '-map', '[v]', '-c:v', 'libx264',
               '-preset', 'medium', '-crf', '18',
               '-pix_fmt', 'yuv420p', '-y', str(output_file)]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Loop created: {output_file.name}")
            return str(output_file)
        except:
            print("❌ Failed to create loop")
            return None

    def step2_multiply_loop(self, loop_file: str, repetitions: int = 10) -> str:
        """Step 2: Multiply loop for longer duration"""
        print("\n" + "="*70)
        print(f"STEP 2: Multiplying Loop (x{repetitions})")
        print("="*70)

        output_file = self.output_dir / f"step2_multiplied_x{repetitions}.mp4"

        # Create concat file
        concat_file = self.output_dir / "concat_list.txt"
        abs_path = Path(loop_file).absolute()

        with open(concat_file, 'w') as f:
            for _ in range(repetitions):
                f.write(f"file '{abs_path}'\n")

        cmd = ['ffmpeg', '-f', 'concat', '-safe', '0',
               '-i', str(concat_file),
               '-c', 'copy', '-y', str(output_file)]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            final_duration = self.info['duration'] * repetitions
            print(f"✅ Multiplied: {output_file.name}")
            print(f"   Duration: {final_duration:.1f}s ({final_duration/60:.1f} minutes)")
            concat_file.unlink()
            return str(output_file)
        except:
            print("❌ Failed to multiply")
            return None

    def step3_upscale_ffmpeg(self, video_file: str, target_res: str = "1080p") -> str:
        """Step 3: Upscale using FFmpeg (fast)"""
        print("\n" + "="*70)
        print(f"STEP 3: Upscaling to {target_res} (FFmpeg)")
        print("="*70)

        resolutions = {
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '1440p': (2560, 1440),
            '4k': (3840, 2160)
        }
        width, height = resolutions.get(target_res.lower(), (1920, 1080))

        output_file = self.output_dir / f"step3_upscaled_{target_res}.mp4"

        # Lanczos upscaling
        cmd = ['ffmpeg', '-i', video_file,
               '-vf', f'scale={width}:{height}:flags=lanczos',
               '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
               '-c:a', 'copy', '-y', str(output_file)]

        try:
            print(f"⏳ Upscaling to {width}x{height}...")
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Upscaled: {output_file.name}")
            return str(output_file)
        except:
            print("❌ Failed to upscale")
            return None

    def step4_topaz_ai_enhance(self, video_file: str, model: str = "artemis-lq", target_res: str = "4k") -> str:
        """Step 4: AI Enhancement using Topaz Video AI"""
        print("\n" + "="*70)
        print(f"STEP 4: AI Enhancement (Topaz {model.upper()}) → {target_res.upper()}")
        print("="*70)

        if not self.topaz_path:
            print("⚠️  Topaz not found, generating instructions instead...")
            return self._generate_topaz_instructions(video_file, model, target_res)

        resolutions = {
            '720p': '1280x720',
            '1080p': '1920x1080',
            '1440p': '2560x1440',
            '4k': '3840x2160'
        }
        resolution = resolutions.get(target_res.lower(), '3840x2160')

        output_file = self.output_dir / f"step4_topaz_{model}_{target_res}.mp4"

        # Try Topaz CLI (may not work in all versions)
        cmd = [
            self.topaz_path,
            '-i', video_file,
            '-o', str(output_file),
            '-m', model,
            '-s', resolution,
            '--quality', 'high'
        ]

        print(f"⏳ Running Topaz AI (this may take a while)...")
        print(f"   Model: {model}")
        print(f"   Target: {resolution}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            if result.returncode == 0:
                print(f"✅ AI Enhanced: {output_file.name}")
                return str(output_file)
            else:
                print("⚠️  Topaz CLI failed, generating manual instructions...")
                return self._generate_topaz_instructions(video_file, model, target_res)
        except subprocess.TimeoutExpired:
            print("⏱️  Topaz is still processing (taking longer than expected)")
            print("   Check Topaz Video AI application for progress")
            return None
        except:
            print("⚠️  Topaz CLI not available, use GUI instead")
            return self._generate_topaz_instructions(video_file, model, target_res)

    def _generate_topaz_instructions(self, video_file: str, model: str, target_res: str) -> str:
        """Generate instructions for manual Topaz processing"""
        instructions_file = self.output_dir / "TOPAZ_MANUAL_INSTRUCTIONS.txt"

        instructions = f"""
╔══════════════════════════════════════════════════════════╗
║  TOPAZ VIDEO AI - MANUAL PROCESSING INSTRUCTIONS        ║
╚══════════════════════════════════════════════════════════╝

📁 Input File:
   {Path(video_file).absolute()}

🎯 SETTINGS TO USE:

1. Open Topaz Video AI

2. Drag and drop the file above

3. AI Model:
   ┌─────────────────────────────────────┐
   │ Model: {model.upper()}              │
   │                                     │
   │ Enhancement: HIGH                   │
   │ Recover Details: ON                 │
   │ Sharpen: MEDIUM                     │
   │ Reduce Noise: {'HIGH' if model == 'artemis-lq' else 'MEDIUM'}                  │
   │                                     │
   │ Deblock: {'HIGH' if model == 'artemis-lq' else 'MEDIUM'}                       │
   │ Compression Artifacts: {'HIGH' if model == 'artemis-lq' else 'LOW'}            │
   └─────────────────────────────────────┘

4. Output Settings:
   ┌─────────────────────────────────────┐
   │ Resolution: {target_res.upper()}                    │
   │ Encoder: H.264 or H.265             │
   │ Quality: CRF 18 (high quality)      │
   │ Preset: SLOW                        │
   └─────────────────────────────────────┘

5. Output Folder:
   {self.output_dir.absolute()}

6. Click "Export" and wait for processing

💡 TIPS:
- Use Preview to test settings on 10 seconds first
- For best quality: CRF 18, Preset SLOW
- Don't use Frame Interpolation for loops
- Estimated time: {self._estimate_topaz_time(video_file)}

═══════════════════════════════════════════════════════════
"""

        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        print(f"📄 Manual instructions saved: {instructions_file.name}")
        print("\n💡 Open Topaz Video AI GUI and follow instructions")
        return None

    def _estimate_topaz_time(self, video_file: str) -> str:
        """Estimate Topaz processing time"""
        try:
            probe = subprocess.run(['ffprobe', '-v', 'error',
                                    '-show_entries', 'format=duration',
                                    '-of', 'json', video_file],
                                   capture_output=True, text=True)
            duration = float(json.loads(probe.stdout)['format']['duration'])

            if duration < 60:
                return "10-30 minutes"
            elif duration < 300:
                return "30-90 minutes"
            elif duration < 600:
                return "1-3 hours"
            else:
                return f"{duration/1800:.0f}-{duration/900:.0f} hours"
        except:
            return "Unknown"

    def run_full_pipeline(self, overlap: float = 2.0, repetitions: int = 10,
                          upscale: str = "1080p", topaz_model: str = "artemis-lq",
                          topaz_res: str = "4k", skip_topaz: bool = False) -> Dict[str, str]:
        """
        Run complete pipeline:
        1. Create seamless loop
        2. Multiply for long duration
        3. Upscale with FFmpeg
        4. AI enhance with Topaz (optional)
        """
        print("\n" + "="*70)
        print("🎬 MASTER VIDEO PIPELINE - FULL WORKFLOW")
        print("="*70)

        results = {}

        # Step 1: Create loop
        loop_file = self.step1_create_seamless_loop(overlap)
        if not loop_file:
            return results
        results['loop'] = loop_file

        # Step 2: Multiply
        multiplied_file = self.step2_multiply_loop(loop_file, repetitions)
        if not multiplied_file:
            return results
        results['multiplied'] = multiplied_file

        # Step 3: FFmpeg upscale
        upscaled_file = self.step3_upscale_ffmpeg(multiplied_file, upscale)
        if not upscaled_file:
            return results
        results['upscaled'] = upscaled_file

        # Step 4: Topaz AI (if not skipped)
        if not skip_topaz:
            topaz_file = self.step4_topaz_ai_enhance(upscaled_file, topaz_model, topaz_res)
            if topaz_file:
                results['topaz'] = topaz_file

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Master Video Pipeline - Complete Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
COMPLETE WORKFLOW:
  1. Create seamless loop (DaVinci technique)
  2. Multiply loop for long duration
  3. Upscale with FFmpeg (fast)
  4. AI enhance with Topaz (best quality)

Examples:
  # Full pipeline: Loop → x10 → 1080p → Topaz 4K
  python master_video_pipeline.py water.mp4

  # Custom settings
  python master_video_pipeline.py water.mp4 -o 2.5 -r 20 -u 1440p -t artemis-lq -tr 4k

  # Skip Topaz (FFmpeg only, faster)
  python master_video_pipeline.py water.mp4 --skip-topaz

  # Just loop creation
  python master_video_pipeline.py water.mp4 -r 1 --skip-topaz

Topaz Models:
  artemis-lq  - Low quality source (YouTube, compressed)
  artemis-mq  - Medium quality
  artemis-hq  - High quality source
  proteus     - Realistic enhancement
        """
    )

    parser.add_argument('input', help='Input video file')
    parser.add_argument('-o', '--overlap', type=float, default=2.0,
                        help='Loop overlap duration (default: 2.0s)')
    parser.add_argument('-r', '--repetitions', type=int, default=10,
                        help='Loop repetitions (default: 10)')
    parser.add_argument('-u', '--upscale', default='1080p',
                        choices=['720p', '1080p', '1440p', '4k'],
                        help='FFmpeg upscale target (default: 1080p)')
    parser.add_argument('-t', '--topaz-model', default='artemis-lq',
                        choices=['artemis-lq', 'artemis-mq', 'artemis-hq', 'proteus'],
                        help='Topaz AI model (default: artemis-lq)')
    parser.add_argument('-tr', '--topaz-res', default='4k',
                        choices=['1080p', '1440p', '4k'],
                        help='Topaz target resolution (default: 4k)')
    parser.add_argument('--skip-topaz', action='store_true',
                        help='Skip Topaz AI step (FFmpeg only)')
    parser.add_argument('-d', '--output-dir', default='master_output')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return

    pipeline = MasterVideoPipeline(args.input, args.output_dir)

    results = pipeline.run_full_pipeline(
        overlap=args.overlap,
        repetitions=args.repetitions,
        upscale=args.upscale,
        topaz_model=args.topaz_model,
        topaz_res=args.topaz_res,
        skip_topaz=args.skip_topaz
    )

    # Final summary
    print("\n" + "="*70)
    print("🎉 PIPELINE COMPLETE!")
    print("="*70)

    for step, file_path in results.items():
        if file_path:
            file_size = Path(file_path).stat().st_size / (1024 * 1024)
            print(f"✅ {step.upper()}: {Path(file_path).name} ({file_size:.1f} MB)")

    if 'topaz' in results and results['topaz']:
        print("\n🏆 FINAL OUTPUT: " + Path(results['topaz']).name)
    elif 'upscaled' in results:
        print("\n🏆 FINAL OUTPUT: " + Path(results['upscaled']).name)

    print("\n💡 All files saved in: " + str(Path(args.output_dir).absolute()))


if __name__ == '__main__':
    main()
