#!/usr/bin/env python3
"""
Topaz AI Video Enhancer - Automated Workflow
Deep AI analysis and enhancement using Topaz Video AI with optimal settings
"""

import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import List, Dict
import shutil


class TopazAIEnhancer:
    def __init__(self, input_video: str, output_dir: str = "topaz_enhanced"):
        self.input_video = input_video
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Get video info
        self.info = self._get_video_info()
        print(f"📹 Input: {self.info['width']}x{self.info['height']} @ {self.info['fps']:.2f} fps")
        print(f"⏱️  Duration: {self.info['duration']:.2f}s")
        print(f"📊 Bitrate: {self.info['bitrate'] / 1000:.0f} kbps")

        # Detect Topaz
        self.topaz_path = self._find_topaz()
        if self.topaz_path:
            print(f"✅ Topaz found: {self.topaz_path}")
        else:
            print("⚠️  Topaz Video AI not found - will generate instructions")

    def _get_video_info(self) -> Dict:
        """Get detailed video information"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,bit_rate',
            '-show_entries', 'format=duration',
            '-of', 'json',
            self.input_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        stream = data['streams'][0]
        fps_parts = stream['r_frame_rate'].split('/')
        fps = float(fps_parts[0]) / float(fps_parts[1])

        return {
            'width': stream['width'],
            'height': stream['height'],
            'fps': fps,
            'duration': float(data['format'].get('duration', 0)),
            'bitrate': int(stream.get('bit_rate', 0))
        }

    def _find_topaz(self) -> str:
        """Find Topaz Video AI installation"""
        paths = [
            'C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\tvai.exe',
            'C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\Topaz Video AI.exe',
            str(Path.home() / 'TopazVideoAIPortable' / 'tvai.exe'),
            '/Applications/Topaz Video AI.app/Contents/MacOS/Topaz Video AI',
        ]

        for path in paths:
            if Path(path).exists():
                return path
        return None

    def analyze_video_quality(self) -> Dict:
        """
        Analyze video to determine best Topaz model and settings
        """
        print("\n🔬 Analyzing video quality...")

        analysis = {
            'resolution': f"{self.info['width']}x{self.info['height']}",
            'quality_score': 0,
            'recommended_model': '',
            'recommended_settings': {}
        }

        # Determine quality based on resolution and bitrate
        pixels = self.info['width'] * self.info['height']
        bitrate_per_pixel = self.info['bitrate'] / pixels if pixels > 0 else 0

        # Quality scoring
        if self.info['width'] <= 720 or self.info['height'] <= 480:
            analysis['quality_score'] = 'LOW'
            analysis['recommended_model'] = 'artemis-lq'
            analysis['reason'] = 'Low resolution (SD/480p)'
        elif bitrate_per_pixel < 0.15:
            analysis['quality_score'] = 'LOW'
            analysis['recommended_model'] = 'artemis-lq'
            analysis['reason'] = 'Low bitrate (compressed/YouTube)'
        elif bitrate_per_pixel < 0.30:
            analysis['quality_score'] = 'MEDIUM'
            analysis['recommended_model'] = 'artemis-mq'
            analysis['reason'] = 'Medium quality source'
        else:
            analysis['quality_score'] = 'HIGH'
            analysis['recommended_model'] = 'artemis-hq'
            analysis['reason'] = 'High quality source'

        # Target resolution recommendation
        if self.info['width'] < 1280:
            analysis['target_resolution'] = '1080p'
        elif self.info['width'] < 1920:
            analysis['target_resolution'] = '1080p'
        elif self.info['width'] < 2560:
            analysis['target_resolution'] = '4k'
        else:
            analysis['target_resolution'] = '4k'

        print(f"  Quality: {analysis['quality_score']}")
        print(f"  Reason: {analysis['reason']}")
        print(f"  Recommended Model: {analysis['recommended_model']}")
        print(f"  Target Resolution: {analysis['target_resolution']}")

        return analysis

    def create_topaz_preset_file(self, analysis: Dict, preset_name: str = "auto") -> str:
        """Create Topaz preset JSON file"""
        preset_file = self.output_dir / f"topaz_preset_{preset_name}.json"

        # Topaz preset configuration
        preset = {
            "version": "1.0",
            "model": analysis['recommended_model'],
            "settings": {
                "enhancement": "high",
                "noise_reduction": "medium" if analysis['quality_score'] == 'LOW' else "low",
                "sharpen": "medium",
                "grain": "none",
                "deblock": "high" if analysis['quality_score'] == 'LOW' else "medium"
            }
        }

        with open(preset_file, 'w') as f:
            json.dump(preset, f, indent=2)

        return str(preset_file)

    def generate_topaz_instructions(self, analysis: Dict) -> str:
        """Generate detailed instructions for manual Topaz processing"""
        instructions_file = self.output_dir / "TOPAZ_INSTRUCTIONS.txt"

        target_res = analysis['target_resolution']
        model = analysis['recommended_model']

        model_descriptions = {
            'artemis-lq': 'Artemis LQ - Low Quality Enhancement (for compressed/YouTube videos)',
            'artemis-mq': 'Artemis MQ - Medium Quality Enhancement',
            'artemis-hq': 'Artemis HQ - High Quality Enhancement (for clean sources)',
        }

        instructions = f"""
═══════════════════════════════════════════════════════════
TOPAZ VIDEO AI - ENHANCEMENT INSTRUCTIONS
═══════════════════════════════════════════════════════════

📁 Input File: {Path(self.input_video).name}
📊 Current: {self.info['width']}x{self.info['height']}
🎯 Target: {target_res}
💎 Quality: {analysis['quality_score']}
📝 Reason: {analysis['reason']}

═══════════════════════════════════════════════════════════
RECOMMENDED SETTINGS
═══════════════════════════════════════════════════════════

🤖 AI MODEL: {model_descriptions[model]}

⚙️  SETTINGS TO USE:

1. Open Topaz Video AI

2. Load Video:
   - Drag and drop: {self.input_video}

3. AI Model Settings:
   ┌─────────────────────────────────────────┐
   │ Model: {model.upper()}                  │
   │                                         │
   │ Enhancement: HIGH                       │
   │ ├─ Recover Details: ON                  │
   │ ├─ Sharpen: MEDIUM                      │
   │ └─ Reduce Noise: {'HIGH' if analysis['quality_score'] == 'LOW' else 'MEDIUM'}                    │
   │                                         │
   │ Artifacts Removal:                      │
   │ ├─ Deblock: {'HIGH' if analysis['quality_score'] == 'LOW' else 'MEDIUM'}                        │
   │ ├─ Dehalo: {'MEDIUM' if analysis['quality_score'] == 'LOW' else 'LOW'}                       │
   │ └─ Compression Artifacts: {'HIGH' if analysis['quality_score'] == 'LOW' else 'MEDIUM'}        │
   │                                         │
   │ Advanced:                               │
   │ ├─ Frame Interpolation: OFF             │
   │ ├─ Slow Motion: OFF                     │
   │ └─ Grain: NONE                          │
   └─────────────────────────────────────────┘

4. Output Settings:
   ┌─────────────────────────────────────────┐
   │ Resolution: {target_res.upper()}                       │
   │ Encoder: H.264 / H.265                  │
   │ Quality: CRF 18 (high quality)          │
   │ Preset: SLOW (better compression)       │
   └─────────────────────────────────────────┘

5. Export:
   - Output folder: {self.output_dir}
   - Click "Export" and wait

═══════════════════════════════════════════════════════════
ALTERNATIVE MODELS (if result not satisfactory)
═══════════════════════════════════════════════════════════

🔄 Try these in order if first doesn't work well:

1. PROTEUS (Realistic Enhancement)
   - Best for: Natural video, people, landscapes
   - Settings: Enhancement HIGH, Sharpen MEDIUM

2. NYX (Detail Enhancement)
   - Best for: Maximum detail, textures
   - Settings: Enhancement HIGH, Sharpen HIGH

3. IRIS (Old Footage Restoration)
   - Best for: Old video, VHS, interlaced
   - Settings: Deinterlace ON, Enhancement HIGH

═══════════════════════════════════════════════════════════
TIPS FOR BEST RESULTS
═══════════════════════════════════════════════════════════

✅ DO:
- Let Topaz analyze the whole video first
- Use preview to test settings on 5-10 seconds
- Compare multiple models side-by-side
- Use CRF 18-20 for high quality
- Check "Prefer Speed" OFF for best quality

❌ DON'T:
- Don't use frame interpolation for loops
- Don't over-sharpen (creates halos)
- Don't use slow-motion features
- Don't add grain to clean footage

═══════════════════════════════════════════════════════════
PROCESSING TIME ESTIMATE
═══════════════════════════════════════════════════════════

Video Length: {self.info['duration']:.0f} seconds
Estimated Time: {self._estimate_processing_time(self.info['duration'])}

(Depends on GPU: RTX 3060 = 1-2x real-time, RTX 4090 = 3-5x)

═══════════════════════════════════════════════════════════
"""

        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        print(f"\n📄 Instructions saved: {instructions_file}")
        return str(instructions_file)

    def _estimate_processing_time(self, duration: float) -> str:
        """Estimate Topaz processing time"""
        # Rough estimates
        if duration < 30:
            return "5-15 minutes"
        elif duration < 60:
            return "15-30 minutes"
        elif duration < 180:
            return "30-90 minutes"
        elif duration < 600:
            return "1.5-3 hours"
        else:
            return f"{duration/600:.1f}-{duration/300:.1f} hours"

    def create_comparison_grid(self, original: str, enhanced: str, output: str = None):
        """Create side-by-side comparison video"""
        if output is None:
            output = self.output_dir / "comparison_grid.mp4"

        print(f"\n🎬 Creating comparison grid...")

        cmd = [
            'ffmpeg',
            '-i', original,
            '-i', enhanced,
            '-filter_complex',
            '[0:v]scale=1280:720,drawtext=text=\'Original\':x=10:y=10:fontsize=32:fontcolor=white[v0];'
            '[1:v]scale=1280:720,drawtext=text=\'Topaz AI Enhanced\':x=10:y=10:fontsize=32:fontcolor=white[v1];'
            '[v0][v1]hstack[out]',
            '-map', '[out]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            '-y', str(output)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Comparison created: {output}")
            return str(output)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create comparison: {e}")
            return None

    def run_analysis(self):
        """Run full analysis and generate instructions"""
        print("\n" + "="*60)
        print("TOPAZ AI VIDEO ENHANCEMENT - AUTO ANALYSIS")
        print("="*60)

        # Analyze video
        analysis = self.analyze_video_quality()

        # Generate preset
        preset_file = self.create_topaz_preset_file(analysis)
        print(f"\n💾 Preset saved: {preset_file}")

        # Generate instructions
        instructions = self.generate_topaz_instructions(analysis)

        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\n📖 Read instructions: {instructions}")
        print(f"🎯 Recommended Model: {analysis['recommended_model'].upper()}")
        print(f"📐 Target Resolution: {analysis['target_resolution'].upper()}")
        print("\n💡 Open Topaz Video AI and follow the instructions above")
        print("💡 Or use the preset file for automated processing")

        return analysis


def main():
    parser = argparse.ArgumentParser(
        description='Topaz AI Video Enhancer - Automated Analysis & Instructions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze video and get Topaz instructions
  python topaz_ai_enhancer.py video.mp4

  # Analyze and specify output directory
  python topaz_ai_enhancer.py video.mp4 -d topaz_output

  # Create comparison of original vs enhanced (after Topaz processing)
  python topaz_ai_enhancer.py video.mp4 --compare enhanced_video.mp4

What this does:
  1. Analyzes video quality (resolution, bitrate, compression)
  2. Recommends optimal Topaz AI model and settings
  3. Generates detailed instructions for manual processing
  4. Creates preset file for batch processing
  5. Estimates processing time

Note: This tool generates instructions for Topaz Video AI.
      You need to have Topaz Video AI installed separately.
        """
    )

    parser.add_argument('input', help='Input video file')
    parser.add_argument('-d', '--output-dir', default='topaz_enhanced',
                        help='Output directory (default: topaz_enhanced)')
    parser.add_argument('-c', '--compare', metavar='ENHANCED',
                        help='Create comparison grid with enhanced video')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return

    # Create enhancer
    enhancer = TopazAIEnhancer(args.input, args.output_dir)

    # Run analysis
    analysis = enhancer.run_analysis()

    # Create comparison if enhanced video provided
    if args.compare:
        if os.path.exists(args.compare):
            enhancer.create_comparison_grid(args.input, args.compare)
        else:
            print(f"\n⚠️  Enhanced video not found: {args.compare}")

    print("\n🎬 Next steps:")
    print("  1. Open Topaz Video AI")
    print("  2. Follow instructions in TOPAZ_INSTRUCTIONS.txt")
    print("  3. Export enhanced video")
    print("  4. Use video_upscaler.py for additional variants if needed")


if __name__ == '__main__':
    main()
