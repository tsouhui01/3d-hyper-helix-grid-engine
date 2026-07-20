"""3D Hyper-Helix Grid Engine｜純 Python 霓虹雙螺旋動畫。"""

from __future__ import annotations

import argparse
import colorsys
import math
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    width: int = 900
    height: int = 900
    points: int = 150
    turns: float = 5.5
    fps: int = 30
    camera: float = 8.5
    scale: float = 285.0


def rgb_hex(hue: float, saturation: float = 0.82, value: float = 1.0) -> str:
    red, green, blue = colorsys.hsv_to_rgb(hue % 1.0, saturation, value)
    return f"#{round(red * 255):02x}{round(green * 255):02x}{round(blue * 255):02x}"


def rotate_project(x: float, y: float, z: float, phase: float, config: Config):
    """旋轉空間座標，再以透視法投影至畫布。"""
    yaw = phase * 0.72
    pitch = 0.42 + math.sin(phase * 0.35) * 0.12
    x, z = x * math.cos(yaw) + z * math.sin(yaw), -x * math.sin(yaw) + z * math.cos(yaw)
    y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)
    depth = max(2.2, config.camera + z)
    factor = config.scale / depth
    return config.width / 2 + x * factor, config.height / 2 - y * factor, factor


def helix_points(phase: float, config: Config):
    """建立兩條互相纏繞、半徑呼吸變化的 3D 螺旋。"""
    strands = [[], []]
    for index in range(config.points):
        progress = index / (config.points - 1)
        z = (progress - 0.5) * 8.0
        angle = progress * math.tau * config.turns + phase
        radius = 2.0 + 0.30 * math.sin(progress * math.tau * 3.0 + phase * 1.4)
        for strand in range(2):
            theta = angle + strand * math.pi
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            strands[strand].append((*rotate_project(x, y, z, phase, config), progress))
    return strands


class HyperHelixApp:
    def __init__(self, config: Config):
        self.config = config
        self.phase = 0.0
        self.running = True
        self.root = tk.Tk()
        self.root.title("Python｜3D Hyper-Helix Grid Engine（Esc 離開）")
        self.root.geometry(f"{config.width}x{config.height}")
        self.root.configure(bg="black")
        self.root.bind("<Escape>", self.close)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas = tk.Canvas(
            self.root, width=config.width, height=config.height,
            bg="#02030a", highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_text(
            28, 26, anchor="nw", text="3D HYPER-HELIX GRID ENGINE",
            fill="#70fff3", font=("Consolas", 17, "bold"), tags="header",
        )
        self.canvas.create_text(
            30, 57, anchor="nw", text="ESC  離開  ·  持續循環運算中",
            fill="#657391", font=("Microsoft JhengHei UI", 10), tags="header",
        )

    def close(self, _event=None):
        self.running = False
        self.root.destroy()

    def draw_frame(self):
        if not self.running:
            return
        self.canvas.delete("frame")
        strands = helix_points(self.phase, self.config)

        # 橫向能量梯：每隔數點連接雙股螺旋，形成 3D 網格。
        for index in range(0, self.config.points, 3):
            a, b = strands[0][index], strands[1][index]
            hue = a[3] * 0.82 + self.phase * 0.025
            self.canvas.create_line(a[0], a[1], b[0], b[1], fill=rgb_hex(hue, 0.72, 0.72), width=1, tags="frame")

        # 先畫遠端，再畫近端，讓景深遮擋更自然。
        particles = []
        for strand_index, strand in enumerate(strands):
            for index, point in enumerate(strand):
                x, y, factor, progress = point
                particles.append((factor, strand_index, index, x, y, progress))
            for left, right in zip(strand, strand[1:]):
                hue = left[3] * 0.82 + strand_index * 0.08 + self.phase * 0.025
                self.canvas.create_line(left[0], left[1], right[0], right[1], fill=rgb_hex(hue, 0.78, 0.68), width=1, tags="frame")

        for factor, strand_index, index, x, y, progress in sorted(particles):
            pulse = 1.0 + 0.35 * math.sin(self.phase * 3.0 + index * 0.32)
            radius = max(1.2, factor * 0.045 * pulse)
            hue = progress * 0.82 + strand_index * 0.08 + self.phase * 0.025
            glow = rgb_hex(hue, 0.75, 0.38)
            color = rgb_hex(hue)
            self.canvas.create_oval(x-radius*2, y-radius*2, x+radius*2, y+radius*2, outline=glow, tags="frame")
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="", tags="frame")

        self.phase = (self.phase + 0.035) % math.tau
        self.root.after(round(1000 / self.config.fps), self.draw_frame)

    def run(self, close_after_ms: int | None = None):
        if close_after_ms is not None:
            self.root.after(close_after_ms, self.close)
        self.draw_frame()
        self.root.mainloop()


def export_svg(output: Path, config: Config, phase: float = 0.7):
    strands = helix_points(phase, config)
    elements = [f'<rect width="{config.width}" height="{config.height}" fill="#02030a"/>']
    for index in range(0, config.points, 3):
        a, b = strands[0][index], strands[1][index]
        elements.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{rgb_hex(a[3]*.82, .72, .72)}"/>')
    for strand_index, strand in enumerate(strands):
        for index, (x, y, factor, progress) in enumerate(strand):
            hue = progress * .82 + strand_index * .08 + phase * .025
            radius = max(1.2, factor * .045)
            if index:
                previous = strand[index - 1]
                elements.append(f'<line x1="{previous[0]:.1f}" y1="{previous[1]:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{rgb_hex(hue,.78,.68)}"/>')
            elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{rgb_hex(hue)}"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{config.width}" height="{config.height}" viewBox="0 0 {config.width} {config.height}">{"".join(elements)}</svg>'
    output.write_text(svg, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="3D Hyper-Helix Grid Engine")
    parser.add_argument("--export-svg", type=Path, help="匯出靜態 SVG 預覽")
    parser.add_argument("--check", action="store_true", help="執行無視窗核心檢查")
    parser.add_argument("--smoke-test", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    config = Config()
    if args.check:
        strands = helix_points(0.0, config)
        assert len(strands) == 2 and all(len(item) == config.points for item in strands)
        print("核心檢查通過：雙股螺旋座標與透視投影正常。")
    elif args.export_svg:
        export_svg(args.export_svg, config)
        print(f"已輸出：{args.export_svg.resolve()}")
    else:
        HyperHelixApp(config).run(close_after_ms=700 if args.smoke_test else None)


if __name__ == "__main__":
    main()
