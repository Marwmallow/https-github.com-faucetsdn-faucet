#!/usr/bin/env python3
"""
Video Upscaler with Multiple AI & Traditional Methods
Automatically creates 5+ upscaled variants with different optimal settings.
"""

import subprocess
import argparse
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Tuple


class VideoUpscaler:
    def __init__(self, input_video: str, output_dir: str = "upscaled", target_resolution: str = "1080p"):
        """
        Initialize VideoUpscaler

        Args:
            input_video: Path to input video file
            output_dir: Directory for output files
            target_resolution: Target resolution (1080p, 1440p, 4k)
        """
        self.input_video = input_video
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Parse target resolution
        self.target_width, self.target_height = self._parse_resolution(target_resolution)

        # Get input video info
        self.input_info = self._get_video_info()
        print(f"Input: {self.input_info['width']}x{self.input_info['height']} @ {self.input_info['fps']} fps")
        print(f"Target: {self.target_width}x{self.target_height}")

        # Check available tools
        self.available_tools = self._check_available_tools()
        print(f"\n🔧 Available tools: {', '.join(self.available_tools)}")

    def _parse_resolution(self, resolution: str) -> Tuple[int, int]:
        """Parse resolution string to width/height"""
        resolutions = {
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '1440p': (2560, 1440),
            '2k': (2560, 1440),
            '4k': (3840, 2160),
            'uhd': (3840, 2160),
        }

        if resolution.lower() in resolutions:
            return resolutions[resolution.lower()]

        # Try to parse custom resolution like "1920x1080"
        if 'x' in resolution:
            try:
                w, h = resolution.lower().split('x')
                return int(w), int(h)
            except:
                pass

        # Default to 1080p
        print(f"⚠️  Unknown resolution '{resolution}', defaulting to 1080p")
        return 1920, 1080

    def _get_video_info(self) -> Dict:
        """Get video information using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,codec_name',
            '-of', 'json',
            self.input_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        stream = data['streams'][0]

        # Parse frame rate
        fps_parts = stream['r_frame_rate'].split('/')
        fps = float(fps_parts[0]) / float(fps_parts[1])

        return {
            'width': stream['width'],
            'height': stream['height'],
            'fps': fps,
            'codec': stream.get('codec_name', 'unknown')
        }

    def _check_available_tools(self) -> List[str]:
        """Check which upscaling tools are available"""
        tools = []

        # Check FFmpeg
        if shutil.which('ffmpeg'):
            tools.append('ffmpeg')

        # Check Topaz Video AI (common locations)
        topaz_paths = [
            'C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\ffmpeg.exe',
            'C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\tvai.exe',
            '/Applications/Topaz Video AI.app/Contents/MacOS/Topaz Video AI',
            str(Path.home() / 'TopazVideoAIPortable' / 'tvai.exe'),
        ]

        for path in topaz_paths:
            if Path(path).exists():
                tools.append('topaz')
                self.topaz_path = path
                break

        # Check Real-ESRGAN
        if shutil.which('realesrgan-ncnn-vulkan'):
            tools.append('realesrgan')

        return tools

    def upscale_ffmpeg_lanczos(self, variant_name: str = "lanczos") -> str:
        """
        High-quality Lanczos upscaling (best for sharp details)
        """
        output_file = self.output_dir / f"{variant_name}_{self.target_height}p.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (Lanczos - sharp)")

        filter_complex = f"scale={self.target_width}:{self.target_height}:flags=lanczos"

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',  # High quality
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr.decode()}")
            return None

    def upscale_ffmpeg_bicubic(self, variant_name: str = "bicubic") -> str:
        """
        Bicubic upscaling (smooth, good for video with noise)
        """
        output_file = self.output_dir / f"{variant_name}_{self.target_height}p.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (Bicubic - smooth)")

        filter_complex = f"scale={self.target_width}:{self.target_height}:flags=bicubic"

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr.decode()}")
            return None

    def upscale_ffmpeg_sharpened(self, variant_name: str = "sharpened") -> str:
        """
        Lanczos + sharpening filter (extra sharp details)
        """
        output_file = self.output_dir / f"{variant_name}_{self.target_height}p.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (Lanczos + Sharpen)")

        filter_complex = (
            f"scale={self.target_width}:{self.target_height}:flags=lanczos,"
            "unsharp=5:5:1.0:5:5:0.0"  # Sharpen
        )

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr.decode()}")
            return None

    def upscale_ffmpeg_denoised(self, variant_name: str = "denoised") -> str:
        """
        Lanczos + denoise filter (clean, good for noisy sources)
        """
        output_file = self.output_dir / f"{variant_name}_{self.target_height}p.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (Lanczos + Denoise)")

        filter_complex = (
            f"hqdn3d=4:3:6:4.5,"  # Denoise first
            f"scale={self.target_width}:{self.target_height}:flags=lanczos"
        )

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr.decode()}")
            return None

    def upscale_ffmpeg_enhanced(self, variant_name: str = "enhanced") -> str:
        """
        Lanczos + color enhancement + sharpening (vibrant and sharp)
        """
        output_file = self.output_dir / f"{variant_name}_{self.target_height}p.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (Enhanced colors + sharp)")

        filter_complex = (
            f"scale={self.target_width}:{self.target_height}:flags=lanczos,"
            "eq=contrast=1.1:brightness=0.02:saturation=1.1,"  # Color enhancement
            "unsharp=5:5:0.8:5:5:0.0"  # Moderate sharpening
        )

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(output_file)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr.decode()}")
            return None

    def upscale_topaz_ai(self, model: str = "artemis-lq", variant_name: str = "topaz_ai") -> str:
        """
        Topaz Video AI upscaling (best quality, requires Topaz Video AI installed)

        Models:
        - artemis-lq: Low quality enhancement (best for compressed videos)
        - artemis-mq: Medium quality
        - artemis-hq: High quality source
        - proteus: Realistic enhancement
        - iris: For interlaced/old footage
        """
        if 'topaz' not in self.available_tools:
            print("❌ Topaz Video AI not found")
            return None

        output_file = self.output_dir / f"{variant_name}_{model}_{self.target_height}p.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (Topaz AI - {model})")

        # Topaz CLI command format
        cmd = [
            self.topaz_path,
            '-i', self.input_video,
            '-o', str(output_file),
            '-m', model,
            '-s', f"{self.target_width}x{self.target_height}",
            '--quality', 'high'
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Created: {output_file}")
            return str(output_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Topaz Error: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Topaz CLI might not be available: {e}")
            print("💡 Tip: Use Topaz Video AI GUI manually for best results")
            return None

    def upscale_realesrgan(self, scale: int = 2, variant_name: str = "realesrgan") -> str:
        """
        Real-ESRGAN AI upscaling (excellent for anime and general video)
        Requires: realesrgan-ncnn-vulkan
        """
        if 'realesrgan' not in self.available_tools:
            print("❌ Real-ESRGAN not found")
            print("💡 Install: https://github.com/xinntao/Real-ESRGAN/releases")
            return None

        output_file = self.output_dir / f"{variant_name}_x{scale}_{self.target_height}p.mp4"

        print(f"\n🎬 Creating variant: {variant_name} (Real-ESRGAN AI)")

        # Real-ESRGAN works on image sequences, so we need to:
        # 1. Extract frames
        # 2. Upscale frames
        # 3. Reassemble video

        temp_dir = self.output_dir / "temp_frames"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Extract frames
            print("  Extracting frames...")
            subprocess.run([
                'ffmpeg', '-i', self.input_video,
                '-qscale:v', '1',
                str(temp_dir / 'frame_%06d.png')
            ], check=True, capture_output=True)

            # Upscale with Real-ESRGAN
            print("  Upscaling with AI...")
            upscaled_dir = self.output_dir / "temp_upscaled"
            upscaled_dir.mkdir(exist_ok=True)

            subprocess.run([
                'realesrgan-ncnn-vulkan',
                '-i', str(temp_dir),
                '-o', str(upscaled_dir),
                '-s', str(scale),
                '-f', 'png'
            ], check=True)

            # Reassemble video
            print("  Reassembling video...")
            subprocess.run([
                'ffmpeg',
                '-framerate', str(self.input_info['fps']),
                '-i', str(upscaled_dir / 'frame_%06d.png'),
                '-i', self.input_video,  # For audio
                '-map', '0:v',
                '-map', '1:a?',
                '-c:v', 'libx264',
                '-preset', 'slow',
                '-crf', '18',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-y',
                str(output_file)
            ], check=True, capture_output=True)

            # Cleanup
            shutil.rmtree(temp_dir)
            shutil.rmtree(upscaled_dir)

            print(f"✅ Created: {output_file}")
            return str(output_file)

        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            # Cleanup on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            if upscaled_dir.exists():
                shutil.rmtree(upscaled_dir)
            return None

    def create_all_variants(self, methods: List[str] = None) -> List[str]:
        """
        Create multiple upscaled variants

        Args:
            methods: List of methods to use. Available:
                     'lanczos', 'bicubic', 'sharpened', 'denoised', 'enhanced',
                     'topaz', 'realesrgan'
        """
        if methods is None:
            # Default: 5 FFmpeg variants (always available)
            methods = ['lanczos', 'bicubic', 'sharpened', 'denoised', 'enhanced']

        print(f"\n🎯 Creating {len(methods)} upscaled variants...")
        print(f"Target resolution: {self.target_width}x{self.target_height}")

        output_files = []

        for method in methods:
            if method == 'lanczos':
                result = self.upscale_ffmpeg_lanczos()
            elif method == 'bicubic':
                result = self.upscale_ffmpeg_bicubic()
            elif method == 'sharpened':
                result = self.upscale_ffmpeg_sharpened()
            elif method == 'denoised':
                result = self.upscale_ffmpeg_denoised()
            elif method == 'enhanced':
                result = self.upscale_ffmpeg_enhanced()
            elif method == 'topaz':
                result = self.upscale_topaz_ai()
            elif method == 'realesrgan':
                result = self.upscale_realesrgan()
            else:
                print(f"⚠️  Unknown method: {method}")
                continue

            if result:
                output_files.append(result)

        return output_files


def main():
    parser = argparse.ArgumentParser(
        description='AI Video Upscaler - Create multiple upscaled variants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create 5 default FFmpeg variants to 1080p
  python video_upscaler.py input.mp4

  # Upscale to 4K
  python video_upscaler.py input.mp4 -r 4k

  # Use specific methods
  python video_upscaler.py input.mp4 -m lanczos sharpened enhanced

  # Include Topaz AI (if installed)
  python video_upscaler.py input.mp4 -m lanczos topaz

  # All available methods
  python video_upscaler.py input.mp4 -m lanczos bicubic sharpened denoised enhanced topaz

Available methods:
  lanczos     - Sharp, detailed (recommended for most cases)
  bicubic     - Smooth, good for noisy video
  sharpened   - Extra sharp with unsharp mask
  denoised    - Clean, removes noise before upscaling
  enhanced    - Vibrant colors + sharpening
  topaz       - AI upscaling (requires Topaz Video AI)
  realesrgan  - AI upscaling (requires Real-ESRGAN)
        """
    )

    parser.add_argument('input', help='Input video file')
    parser.add_argument('-r', '--resolution', default='1080p',
                        help='Target resolution: 720p, 1080p, 1440p, 4k (default: 1080p)')
    parser.add_argument('-m', '--methods', nargs='+',
                        help='Upscaling methods to use (default: all FFmpeg methods)')
    parser.add_argument('-d', '--output-dir', default='upscaled',
                        help='Output directory (default: upscaled)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found")
        return

    # Create upscaler
    upscaler = VideoUpscaler(args.input, args.output_dir, args.resolution)

    # Create variants
    output_files = upscaler.create_all_variants(args.methods)

    if output_files:
        print(f"\n✅ Successfully created {len(output_files)} variants:")
        for f in output_files:
            file_size = Path(f).stat().st_size / (1024 * 1024)  # MB
            print(f"  📁 {f} ({file_size:.1f} MB)")
        print(f"\n💡 Compare all variants and choose the best one!")
        print(f"💡 For best AI quality: use Topaz Video AI or Real-ESRGAN")
    else:
        print("\n❌ No variants were created")


if __name__ == '__main__':
    main()
