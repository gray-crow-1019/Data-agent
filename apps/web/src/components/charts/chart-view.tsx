import { useEffect, useRef } from "react";
import * as echarts from "echarts";

export default function ChartView({ option }: { option?: Record<string, unknown> }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    chartRef.current = chart;
    if (option && Object.keys(option).length > 0) {
      const safeOption = {
        grid: {
          left: "10%",
          right: "8%",
          top: 50,
          bottom: 50,
          containLabel: true,
        },
        textStyle: { fontSize: 11 },
        xAxis: { axisLabel: { overflow: "truncate", width: 90, rotate: 15 } },
        yAxis: { axisLabel: { overflow: "truncate", width: 60 } },
      };
      chart.setOption(safeOption as Record<string, unknown>, true);
      chart.setOption(option as Record<string, unknown>, false);
    } else {
      chart.setOption({
        title: { text: "暂无可视化" },
        xAxis: { type: "category", data: [] },
        yAxis: { type: "value" },
        series: [],
      });
    }
    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
      chartRef.current = null;
    };
  }, [option]);

  const handleDownload = () => {
    if (!chartRef.current) return;
    const url = chartRef.current.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: "#ffffff" });
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "chart.png";
    anchor.click();
  };

  return (
    <div className="relative overflow-hidden rounded-3xl border border-[color:var(--border)] bg-gradient-to-br from-white/80 to-white/30 p-6">
      <div className="absolute inset-0 opacity-30">
        <div className="h-full w-full bg-[radial-gradient(circle_at_top,_rgba(14,138,122,0.2),_transparent_60%)]" />
      </div>
      <div className="relative">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium">图表</h3>
            <p className="text-xs text-[color:var(--muted)]">来自后端的 ECharts 配置</p>
          </div>
          <button
            className="rounded-full border border-[color:var(--border)] bg-white/70 px-3 py-1 text-xs"
            onClick={handleDownload}
          >
            下载图表
          </button>
        </div>
        <div ref={ref} className="mt-6 h-64 w-full max-w-full overflow-hidden" />
      </div>
    </div>
  );
}
