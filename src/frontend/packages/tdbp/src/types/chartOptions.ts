export interface BarChartOption {
  tooltip: {
    trigger: string;
    axisPointer: {
      type: "shadow" | "line";
    };
  };
  legend: {
    data?: string[];
  };
  grid: {
    left: string;
    right: string;
    bottom: string;
    containLabel: boolean;
  };
  xAxis: {
    type: string;
    min?: number;
    max?: number;
  };
  yAxis: {
    type: string;
    data: string[];
  };
  series: Array<{
    name: string;
    type: string;
    stack: string;
    label: {
      show: boolean;
      position?: string;
      formatter?: any;
    };
    emphasis: {
      focus: string;
    };
    data: number[];
  }>;
}

export interface RadarChartOption {
  legend: {
    data: string[];
  };
  radar: {
    indicator: Array<{
      name: string;
      max: number;
    }>;
  };
  series: Array<{
    name: string;
    type: string;
    data: Array<{
      value: number[];
      name: string;
    }>;
  }>;
}