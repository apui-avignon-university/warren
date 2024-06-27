export interface BarChartOption {
  tooltip: {
    trigger: string;
    axisPointer: {
      type: "shadow" | "line";
    };
  };
  animation?: boolean;
  legend: {
    data?: string[];
  };
  grid: {
    left: string;
    right: string;
    bottom: string;
    containLabel: boolean;
  };
  dataZoom?: Array<{
    type?: string;
    yAxisIndex?: number;
    zoomLock?: boolean;
    filterMode?: string;
    width?: number;
    right?: number;
    top?: number;
    bottom?: number;
    start?: number;
    end?: number;
    handleSize?: number;
    showDetail?: boolean;
    zoomOnMouseWheel?: false;
    moveOnMouseMove?: true;
    moveOnMouseWheel?: true;
  }>;
  emphasis?: {
    focus: string;
    blurScope: string;
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
    data: Array<{
      value?: number;
      itemStyle?: {
        color?: string;
      };
    }>;
  }>;
}

export interface RadarChartOption {
  tooltip: {
    trigger: string;
    axisPointer: {
      type: "shadow" | "line";
    };
    valueFormatter: (value: number) => string;
  };
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
