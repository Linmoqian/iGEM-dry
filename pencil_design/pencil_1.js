/**
 * @schema 2.11
 */

const COLORS = {
  bg: '$global-bg',
  panel: '$panel-bg',
  border: '$border-color',
  primary: '$primary-blue',
  activeBg: '$active-tab-bg',
  activeText: '$active-tab-text',
  brand: '$text-brand',
  text: '$text-primary',
  muted: '$text-muted',
  secondary: '$text-secondary',
  danger: '$status-danger',
  warning: '$status-warning',
  normal: '$status-normal',
  info: '$status-info',
  offline: '$status-offline',
};

const HEX = {
  primary: '#0ea5e9',
  danger: '#ef4444',
  warning: '#ff7a00',
  normal: '#22c55e',
  info: '#06b6d4',
  offline: '#94a3b8',
  border: '#d0e3f5',
};

const SHADOW_CARD = {
  type: 'shadow',
  shadowType: 'outer',
  offset: { x: 0, y: 6 },
  spread: 0,
  blur: 18,
  color: '#0ea5e914',
};

const SHADOW_PANEL = {
  type: 'shadow',
  shadowType: 'outer',
  offset: { x: 0, y: 10 },
  spread: 0,
  blur: 28,
  color: '#0ea5e914',
};

const devices = [
  {
    id: 'device-1',
    name: '漂华预警-06',
    type: 'buoy',
    status: 'online',
    location: '东湖预警区',
    updatedAt: '09:42',
    battery: 86,
    signalDbm: -58,
    toxin: 6.35,
    waterTemp: 24.8,
    ph: 7.4,
    connection: 'wifi',
    riskLabel: '高风险',
    riskColor: COLORS.danger,
    riskHex: HEX.danger,
    selected: true,
  },
  {
    id: 'device-2',
    name: '入水口探针-02',
    type: 'probe',
    status: 'online',
    location: '北侧入水口',
    updatedAt: '09:40',
    battery: 63,
    signalDbm: -74,
    toxin: 1.36,
    waterTemp: 25.5,
    ph: 7.1,
    connection: 'wifi',
    riskLabel: '警戒',
    riskColor: COLORS.warning,
    riskHex: HEX.warning,
    selected: false,
  },
  {
    id: 'device-3',
    name: '岸线巡检猫-03',
    type: 'sensor',
    status: 'idle',
    location: '西南岸线',
    updatedAt: '09:33',
    battery: 38,
    signalDbm: -83,
    toxin: 0.78,
    waterTemp: 26.1,
    ph: 7.6,
    connection: 'bluetooth',
    riskLabel: '正常',
    riskColor: COLORS.normal,
    riskHex: HEX.normal,
    selected: true,
  },
  {
    id: 'device-4',
    name: '湖心浮标-01',
    type: 'buoy',
    status: 'online',
    location: '湖心采样点',
    updatedAt: '09:41',
    battery: 92,
    signalDbm: -57,
    toxin: 0.42,
    waterTemp: 24.3,
    ph: 7.2,
    connection: 'wifi',
    riskLabel: '关注',
    riskColor: COLORS.info,
    riskHex: HEX.info,
    selected: true,
  },
  {
    id: 'device-5',
    name: '排水口监测-04',
    type: 'probe',
    status: 'idle',
    location: '东南排水口',
    updatedAt: '09:39',
    battery: 71,
    signalDbm: -69,
    toxin: 1.05,
    waterTemp: 25.8,
    ph: 7.7,
    connection: 'wifi',
    riskLabel: '警戒',
    riskColor: COLORS.warning,
    riskHex: HEX.warning,
    selected: true,
  },
  {
    id: 'device-6',
    name: '补给站传感器-05',
    type: 'offline',
    status: 'offline',
    location: '南岸补给站',
    updatedAt: '09:12',
    battery: 14,
    signalDbm: -96,
    toxin: 0.31,
    waterTemp: 23.9,
    ph: 7.3,
    connection: 'none',
    riskLabel: '离线',
    riskColor: COLORS.offline,
    riskHex: HEX.offline,
    selected: true,
  },
];

const comparisonRows = [
  { name: '漂华预警-06', value: '6.35', unit: 'µg/L', color: COLORS.danger },
  { name: '入水口探针-02', value: '1.36', unit: 'µg/L', color: COLORS.warning },
  { name: '岸线巡检猫-03', value: '0.78', unit: 'µg/L', color: COLORS.normal },
  { name: '湖心浮标-01', value: '0.42', unit: 'µg/L', color: COLORS.info },
  { name: '排水口监测-04', value: '1.05', unit: 'µg/L', color: COLORS.warning },
];

function frame(id, x, y, width, height, extra = {}, children = []) {
  return {
    id,
    type: 'frame',
    x,
    y,
    width,
    height,
    layout: 'none',
    clip: false,
    ...extra,
    children,
  };
}

function rect(id, x, y, width, height, extra = {}) {
  return { id, type: 'rectangle', x, y, width, height, ...extra };
}

function ellipse(id, x, y, width, height, extra = {}) {
  return { id, type: 'ellipse', x, y, width, height, ...extra };
}

function textNode(id, x, y, width, height, content, extra = {}) {
  return {
    id,
    type: 'text',
    x,
    y,
    width,
    height,
    content,
    textGrowth: 'auto',
    fontFamily: 'Microsoft YaHei',
    fontSize: 14,
    fontWeight: 500,
    fill: COLORS.text,
    ...extra,
  };
}

function iconNode(id, x, y, size, icon, fill = COLORS.text, extra = {}) {
  return {
    id,
    type: 'icon_font',
    x,
    y,
    width: size,
    height: size,
    iconFontFamily: 'lucide',
    iconFontName: icon,
    fill,
    ...extra,
  };
}

function navItem(id, x, label, icon, active = false) {
  return frame(
    id,
    0,
    124,
    42,
    {
      fill: active ? COLORS.activeBg : '#ffffff00',
      cornerRadius: 18,
      layout: 'horizontal',
      gap: 6,
      alignItems: 'center',
      justifyContent: 'center',
      padding: [0, 14],
      stroke: active ? { thickness: 1, fill: COLORS.activeBg } : undefined,
    },
    [
      iconNode(`${id}/icon`, 0, 0, 16, icon, active ? COLORS.activeText : COLORS.secondary),
      textNode(`${id}/label`, 0, 0, 76, 18, label, {
        fontSize: 13,
        fontWeight: active ? 700 : 600,
        fill: active ? COLORS.activeText : COLORS.secondary,
      }),
    ],
  );
}

function topButton(id, x, label, icon, variant = 'secondary', width = 122) {
  const primary = variant === 'primary';
  return frame(
    id,
    x,
    0,
    width,
    40,
    {
      fill: primary ? COLORS.primary : COLORS.panel,
      cornerRadius: 10,
      layout: 'horizontal',
      gap: 8,
      alignItems: 'center',
      justifyContent: 'center',
      padding: [0, 16],
      stroke: { thickness: 1, fill: primary ? COLORS.primary : COLORS.border },
      effect: SHADOW_CARD,
    },
    [
      iconNode(`${id}/icon`, 0, 0, 16, icon, primary ? '#ffffff' : COLORS.primary),
      textNode(`${id}/label`, 0, 0, width - 36, 18, label, {
        fontSize: 13,
        fontWeight: 700,
        fill: primary ? '#ffffff' : COLORS.text,
      }),
    ],
  );
}

function metricBox(id, x, y, width, height, label, value, unit, color, riskLabel, accentHex) {
  return frame(
    id,
    x,
    y,
    width,
    height,
    {
      fill: '#f8fbff',
      cornerRadius: 14,
      stroke: { thickness: 1, fill: COLORS.border },
    },
    [
      textNode(`${id}/label`, 10, 8, width - 20, 16, label, {
        fontSize: 10,
        fontWeight: 700,
        fill: COLORS.muted,
      }),
      textNode(`${id}/value`, 10, 32, width - 20, 30, value, {
        fontSize: width < 86 ? 20 : 22,
        fontWeight: 800,
        fill: color,
      }),
      textNode(`${id}/unit`, 10, 60, width - 20, 16, unit, {
        fontSize: 10,
        fontWeight: 700,
        fill: COLORS.muted,
      }),
      frame(
        `${id}/badge`,
        width - 54,
        8,
        44,
        18,
        {
          fill: `${accentHex}1a`,
          cornerRadius: 9,
          stroke: { thickness: 1, fill: `${accentHex}66` },
          layout: 'horizontal',
          alignItems: 'center',
          justifyContent: 'center',
        },
        [
          textNode(`${id}/badge-text`, 0, 0, 44, 14, riskLabel, {
            fontSize: 9,
            fontWeight: 700,
            fill: color,
            textAlign: 'center',
          }),
        ],
      ),
    ],
  );
}

function illustrationPlaceholder(id, x, y, kind, label) {
  const strokeColor =
    kind === 'buoy'
      ? COLORS.primary
      : kind === 'probe'
        ? COLORS.warning
        : kind === 'sensor'
          ? COLORS.normal
          : COLORS.offline;
  const accentHex =
    kind === 'buoy'
      ? HEX.primary
      : kind === 'probe'
        ? HEX.warning
        : kind === 'sensor'
          ? HEX.normal
          : HEX.offline;

  const fillColor =
    kind === 'buoy'
      ? '#e9f4ff'
      : kind === 'probe'
        ? '#fff3e6'
        : kind === 'sensor'
          ? '#ecfbf4'
          : '#eef2f7';

  const children = [];

  if (kind === 'buoy') {
    children.push(
      ellipse(`${id}/orb`, 23, 14, 46, 46, {
        fill: '#dceeff',
        stroke: { thickness: 2, fill: strokeColor },
      }),
      rect(`${id}/mast`, 42, 8, 6, 18, {
        fill: strokeColor,
        cornerRadius: 3,
      }),
      ellipse(`${id}/wave1`, 17, 46, 58, 18, {
        fill: '#ffffff00',
        stroke: { thickness: 2, fill: strokeColor },
      }),
      ellipse(`${id}/wave2`, 24, 52, 44, 14, {
        fill: '#ffffff00',
        stroke: { thickness: 1.5, fill: strokeColor },
      }),
    );
  }

  if (kind === 'probe') {
    children.push(
      rect(`${id}/body`, 36, 10, 20, 48, {
        fill: fillColor,
        cornerRadius: 10,
        stroke: { thickness: 2, fill: strokeColor },
      }),
      ellipse(`${id}/head`, 35, 6, 22, 14, {
        fill: '#ffffff',
        stroke: { thickness: 2, fill: strokeColor },
      }),
      rect(`${id}/pipe`, 27, 22, 8, 34, {
        fill: '#ffffff00',
        cornerRadius: 4,
        stroke: { thickness: 1.5, fill: strokeColor, dashPattern: [4, 4] },
      }),
      ellipse(`${id}/dot`, 40, 62, 12, 12, {
        fill: `${accentHex}33`,
        stroke: { thickness: 1, fill: strokeColor },
      }),
    );
  }

  if (kind === 'sensor') {
    children.push(
      rect(`${id}/box`, 30, 16, 32, 38, {
        fill: fillColor,
        cornerRadius: 8,
        stroke: { thickness: 2, fill: strokeColor },
      }),
      rect(`${id}/slot`, 38, 24, 16, 16, {
        fill: '#ffffff',
        cornerRadius: 4,
        stroke: { thickness: 1, fill: strokeColor },
      }),
      ellipse(`${id}/antenna`, 42, 8, 8, 8, {
        fill: strokeColor,
      }),
      rect(`${id}/base`, 20, 54, 52, 10, {
        fill: '#ffffff00',
        cornerRadius: 5,
        stroke: { thickness: 1.5, fill: strokeColor },
      }),
    );
  }

  if (kind === 'offline') {
    children.push(
      rect(`${id}/body`, 28, 18, 36, 36, {
        fill: fillColor,
        cornerRadius: 10,
        stroke: { thickness: 2, fill: strokeColor, dashPattern: [5, 4] },
      }),
      rect(`${id}/slash`, 40, 10, 6, 54, {
        fill: strokeColor,
        cornerRadius: 3,
        rotation: 35,
        opacity: 0.55,
      }),
      ellipse(`${id}/dot`, 42, 24, 10, 10, {
        fill: '#ffffff',
        stroke: { thickness: 1, fill: strokeColor },
      }),
    );
  }

  children.push(
    textNode(`${id}/label`, 0, 66, 92, 16, label, {
      fontSize: 11,
      fontWeight: 700,
      fill: strokeColor,
      textAlign: 'center',
    }),
  );

  return frame(
    id,
    x,
    y,
    92,
    92,
    {
      fill: '#f8fbff',
      cornerRadius: 16,
      stroke: { thickness: 1, fill: `${accentHex}66`, dashPattern: [6, 4] },
    },
    children,
  );
}

function checkBadge(id, x, y) {
  return frame(
    id,
    x,
    y,
    20,
    20,
    {
      fill: COLORS.primary,
      cornerRadius: 10,
      stroke: { thickness: 1, fill: '#ffffff66' },
      effect: SHADOW_CARD,
    },
    [iconNode(`${id}/icon`, 3, 3, 14, 'check', '#ffffff')],
  );
}

function deviceCard(device, x, y) {
  return frame(
    device.id,
    x,
    y,
    310,
    260,
    {
      fill: COLORS.panel,
      cornerRadius: 18,
      stroke: { thickness: 1, fill: COLORS.border },
      effect: SHADOW_CARD,
    },
    [
      illustrationPlaceholder(
        `${device.id}/illustration`,
        16,
        16,
        device.type,
        device.type === 'buoy' ? '浮标' : device.type === 'probe' ? '探针' : device.type === 'sensor' ? '传感' : '离线',
      ),
      textNode(`${device.id}/name`, 120, 18, 154, 24, device.name, {
        fontSize: 16,
        fontWeight: 800,
        fill: COLORS.text,
      }),
      frame(
        `${device.id}/status-row`,
        120,
        46,
        140,
        18,
        {
          layout: 'horizontal',
          gap: 6,
          alignItems: 'center',
        },
        [
          ellipse(`${device.id}/status-dot`, 0, 2, 8, 8, {
            fill:
              device.status === 'online'
                ? COLORS.normal
                : device.status === 'idle'
                  ? COLORS.warning
                  : COLORS.offline,
          }),
          textNode(`${device.id}/status`, 0, 0, 70, 16, device.status === 'online' ? '在线' : device.status === 'idle' ? '待机' : '离线', {
            fontSize: 12,
            fontWeight: 700,
            fill:
              device.status === 'online'
                ? COLORS.normal
                : device.status === 'idle'
                  ? COLORS.warning
                  : COLORS.offline,
          }),
          textNode(`${device.id}/updated`, 0, 0, 68, 16, device.updatedAt, {
            fontSize: 11,
            fontWeight: 600,
            fill: COLORS.muted,
          }),
        ],
      ),
      textNode(`${device.id}/location`, 120, 66, 154, 16, device.location, {
        fontSize: 11,
        fontWeight: 600,
        fill: COLORS.muted,
      }),
      frame(
        `${device.id}/conn`,
        236,
        15,
        56,
        22,
        {
          layout: 'horizontal',
          gap: 4,
          alignItems: 'center',
          justifyContent: 'end',
        },
        [
          iconNode(
            `${device.id}/conn-icon`,
            0,
            0,
            18,
            device.connection === 'bluetooth' ? 'bluetooth' : device.connection === 'wifi' ? 'wifi' : 'minus',
            device.connection === 'bluetooth' ? COLORS.primary : device.connection === 'wifi' ? COLORS.normal : COLORS.offline,
          ),
          textNode(`${device.id}/conn-label`, 0, 0, 32, 14, device.connection === 'bluetooth' ? 'BT' : device.connection === 'wifi' ? 'WiFi' : '--', {
            fontSize: 10,
            fontWeight: 700,
            fill: device.connection === 'bluetooth' ? COLORS.primary : device.connection === 'wifi' ? COLORS.normal : COLORS.offline,
          }),
        ],
      ),
      frame(
        `${device.id}/battery`,
        226,
        42,
        74,
        20,
        {
          layout: 'horizontal',
          gap: 4,
          alignItems: 'center',
          justifyContent: 'end',
        },
        [
          iconNode(`${device.id}/battery-icon`, 0, 0, 16, 'battery', COLORS.muted),
          textNode(`${device.id}/battery-text`, 0, 0, 20, 14, `${device.battery}`, {
            fontSize: 11,
            fontWeight: 700,
            fill: COLORS.text,
          }),
          textNode(`${device.id}/battery-unit`, 0, 0, 10, 14, '%', {
            fontSize: 10,
            fontWeight: 700,
            fill: COLORS.muted,
          }),
        ],
      ),
      checkBadge(`${device.id}/check`, 274, 16),
      rect(`${device.id}/divider`, 16, 114, 278, 1, {
        fill: COLORS.border,
      }),
      metricBox(
        `${device.id}/toxin`,
        16,
        126,
        84,
        112,
        '藻毒素',
        device.toxin.toFixed(2),
        'µg/L',
        device.riskColor,
        device.riskLabel,
        device.riskHex,
      ),
      metricBox(
        `${device.id}/temp`,
        108,
        126,
        90,
        112,
        '水温',
        device.waterTemp.toFixed(1),
        '°C',
        COLORS.text,
        '温度',
        HEX.border,
      ),
      metricBox(
        `${device.id}/ph`,
        206,
        126,
        88,
        112,
        'pH',
        device.ph.toFixed(1),
        '',
        COLORS.text,
        '水质',
        HEX.border,
      ),
    ],
  );
}

function radarScanner(id, x, y) {
  return frame(
    id,
    x,
    y,
    280,
    280,
    {
      fill: '#f8fbff',
      cornerRadius: 24,
    },
    [
      ellipse(`${id}/ring-outer`, 0, 0, 280, 280, {
        fill: '#ffffff00',
        stroke: { thickness: 2, fill: '#0ea5e933', dashPattern: [8, 8] },
      }),
      ellipse(`${id}/ring-mid`, 40, 40, 200, 200, {
        fill: '#ffffff00',
        stroke: { thickness: 2, fill: '#0ea5e959', dashPattern: [8, 8] },
      }),
      ellipse(`${id}/ring-inner`, 80, 80, 120, 120, {
        fill: '#ffffff00',
        stroke: { thickness: 2, fill: '#0ea5e980', dashPattern: [8, 8] },
      }),
      ellipse(`${id}/glow`, 104, 104, 72, 72, {
        fill: COLORS.primary,
        opacity: 0.16,
      }),
      ellipse(`${id}/center`, 104, 104, 72, 72, {
        fill: COLORS.primary,
        stroke: { thickness: 1, fill: '#ffffff66' },
        effect: SHADOW_CARD,
      }),
      iconNode(`${id}/bluetooth`, 122, 122, 36, 'bluetooth', '#ffffff'),
      textNode(`${id}/label`, 0, 190, 280, 20, '蓝牙扫描中', {
        fontSize: 12,
        fontWeight: 700,
        fill: COLORS.primary,
        textAlign: 'center',
      }),
      textNode(`${id}/hint`, 0, 212, 280, 16, '信号范围内设备自动浮现', {
        fontSize: 10,
        fontWeight: 600,
        fill: COLORS.muted,
        textAlign: 'center',
      }),
    ],
  );
}

function comparisonRow(row, index) {
  const rowY = 410 + index * 50;
  return frame(
    `comparison-${index}`,
    20,
    rowY,
    306,
    44,
    {
      layout: 'none',
    },
    [
      frame(
        `comparison-${index}/left`,
        0,
        0,
        186,
        44,
        {
          layout: 'vertical',
          gap: 4,
        },
        [
          frame(
            `comparison-${index}/name-row`,
            0,
            0,
            186,
            20,
            {
              layout: 'horizontal',
              gap: 8,
              alignItems: 'center',
            },
            [
              ellipse(`comparison-${index}/dot`, 0, 6, 8, 8, { fill: row.color }),
              textNode(`comparison-${index}/name`, 0, 0, 170, 18, row.name, {
                fontSize: 13,
                fontWeight: 800,
                fill: COLORS.text,
              }),
            ],
          ),
          textNode(`comparison-${index}/sub`, 16, 22, 160, 14, 'RSSI -48 dBm', {
            fontSize: 10,
            fontWeight: 600,
            fill: COLORS.muted,
          }),
        ],
      ),
      frame(
        `comparison-${index}/value`,
        206,
        0,
        100,
        44,
        {
          layout: 'horizontal',
          alignItems: 'center',
          justifyContent: 'end',
          gap: 2,
        },
        [
          textNode(`comparison-${index}/value-text`, 0, 0, 56, 20, row.value, {
            fontSize: 18,
            fontWeight: 800,
            fill: row.color,
          }),
          textNode(`comparison-${index}/unit`, 0, 3, 40, 14, row.unit, {
            fontSize: 10,
            fontWeight: 700,
            fill: COLORS.muted,
          }),
        ],
      ),
      rect(`comparison-${index}/divider`, 0, 43, 306, 1, {
        fill: COLORS.border,
      }),
    ],
  );
}

function sidebarMascot() {
  return frame(
    'sidebar-mascot',
    16,
    632,
    158,
    222,
    {
      fill: '#eaf5ff',
      cornerRadius: 26,
      stroke: { thickness: 1, fill: '#8ec5ff', dashPattern: [6, 4] },
      effect: SHADOW_CARD,
    },
    [
      ellipse('sidebar-mascot/blob', 30, 34, 94, 94, {
        fill: '#dbeeff',
        stroke: { thickness: 1, fill: COLORS.primary },
      }),
      iconNode('sidebar-mascot/flask', 53, 48, 46, 'flask-conical', COLORS.primary),
      ellipse('sidebar-mascot/bubble-1', 24, 18, 8, 8, { fill: '#ffffffaa' }),
      ellipse('sidebar-mascot/bubble-2', 118, 28, 10, 10, { fill: '#ffffffaa' }),
      ellipse('sidebar-mascot/bubble-3', 114, 114, 8, 8, { fill: '#ffffffaa' }),
      iconNode('sidebar-mascot/microscope', 24, 136, 26, 'microscope', COLORS.primary),
      textNode('sidebar-mascot/title', 0, 176, 158, 16, '吉祥物', {
        fontSize: 13,
        fontWeight: 800,
        fill: COLORS.primary,
        textAlign: 'center',
      }),
      textNode('sidebar-mascot/subtitle', 0, 194, 158, 14, '实验器材', {
        fontSize: 10,
        fontWeight: 700,
        fill: COLORS.muted,
        textAlign: 'center',
      }),
    ],
  );
}

function seaweedDecoration() {
  return frame(
    'seaweed-decoration',
    6,
    646,
    172,
    320,
    {
      fill: '#ffffff00',
    },
    [
      rect('seaweed-1', 18, 170, 10, 120, {
        fill: '#bde6d7',
        cornerRadius: 5,
        rotation: -8,
        opacity: 0.85,
      }),
      ellipse('seaweed-1-top', 14, 152, 18, 20, { fill: '#bde6d7', opacity: 0.9 }),
      rect('seaweed-2', 38, 150, 10, 138, {
        fill: '#bde6d7',
        cornerRadius: 5,
        rotation: 6,
        opacity: 0.8,
      }),
      ellipse('seaweed-2-top', 32, 130, 20, 22, { fill: '#bde6d7', opacity: 0.9 }),
      rect('seaweed-3', 58, 176, 10, 114, {
        fill: '#bde6d7',
        cornerRadius: 5,
        rotation: 12,
        opacity: 0.78,
      }),
      ellipse('seaweed-3-top', 54, 156, 18, 20, { fill: '#bde6d7', opacity: 0.88 }),
      rect('seaweed-4', 82, 142, 10, 152, {
        fill: '#bde6d7',
        cornerRadius: 5,
        rotation: 18,
        opacity: 0.72,
      }),
      ellipse('seaweed-4-top', 76, 122, 20, 22, { fill: '#bde6d7', opacity: 0.86 }),
      ellipse('seaweed-bubble-1', 120, 176, 8, 8, { fill: '#ffffffaa' }),
      ellipse('seaweed-bubble-2', 138, 152, 6, 6, { fill: '#ffffffaa' }),
      ellipse('seaweed-bubble-3', 146, 196, 10, 10, { fill: '#ffffffaa' }),
      ellipse('seaweed-bubble-4', 122, 236, 7, 7, { fill: '#ffffffaa' }),
    ],
  );
}

function bottomDecoration() {
  return frame(
    'bottom-decoration',
    1370,
    820,
    180,
    120,
    {
      fill: '#ffffff00',
    },
    [
      frame(
        'bottom-decoration/flask-box',
        42,
        8,
        72,
        72,
        {
          fill: '#eaf5ff',
          cornerRadius: 22,
          stroke: { thickness: 1, fill: '#8ec5ff', dashPattern: [6, 4] },
        },
        [
          iconNode('bottom-decoration/flask', 18, 16, 34, 'flask-conical', COLORS.primary),
        ],
      ),
      frame(
        'bottom-decoration/misc-box',
        90,
        28,
        78,
        78,
        {
          fill: '#eef8ff',
          cornerRadius: 22,
          stroke: { thickness: 1, fill: '#8ec5ff', dashPattern: [6, 4] },
        },
        [
          iconNode('bottom-decoration/microscope', 22, 18, 34, 'microscope', COLORS.primary),
        ],
      ),
      ellipse('bottom-decoration/bubble-1', 6, 6, 12, 12, { fill: '#d5ecff' }),
      ellipse('bottom-decoration/bubble-2', 24, 44, 8, 8, { fill: '#d5ecff' }),
      ellipse('bottom-decoration/bubble-3', 156, 8, 10, 10, { fill: '#d5ecff' }),
      textNode('bottom-decoration/title', 0, 90, 180, 16, '烧杯 / 吉祥物', {
        fontSize: 10,
        fontWeight: 700,
        fill: COLORS.muted,
        textAlign: 'center',
      }),
    ],
  );
}

function headerLogo() {
  return frame(
    'header-logo',
    24,
    16,
    96,
    86,
    {
      fill: '#ffffff00',
    },
    [
      ellipse('header-logo/outer', 12, 0, 72, 72, {
        fill: '#e8f3ff',
        stroke: { thickness: 2, fill: COLORS.primary },
      }),
      ellipse('header-logo/inner', 24, 12, 48, 48, {
        fill: '#ffffff',
        stroke: { thickness: 2, fill: COLORS.primary },
      }),
      ellipse('header-logo/dot-1', 38, 24, 10, 10, { fill: COLORS.primary }),
      ellipse('header-logo/dot-2', 50, 20, 8, 8, { fill: COLORS.info }),
      ellipse('header-logo/dot-3', 46, 36, 6, 6, { fill: COLORS.normal }),
      textNode('header-logo/title', 0, 60, 96, 16, 'AQUA', {
        fontSize: 10,
        fontWeight: 800,
        fill: COLORS.primary,
        textAlign: 'center',
      }),
    ],
  );
}

function buildPage() {
  const header = frame(
    'header',
    0,
    0,
    1586,
    118,
    {
      fill: COLORS.panel,
    },
    [
      headerLogo(),
      textNode('header/title', 122, 24, 280, 28, '水体藻毒素监测平台', {
        fontSize: 22,
        fontWeight: 800,
        fill: COLORS.brand,
      }),
      textNode('header/subtitle', 124, 54, 260, 14, 'Water Algal Toxin Monitoring', {
        fontSize: 10,
        fontWeight: 700,
        fill: COLORS.muted,
      }),
      frame(
        'header/nav-strip',
        500,
        30,
        560,
        52,
        {
          fill: '#f8fbff',
          cornerRadius: 26,
          stroke: { thickness: 1, fill: COLORS.border },
          layout: 'horizontal',
          gap: 6,
          alignItems: 'center',
          padding: [5, 6],
        },
        [
          navItem('header/nav-overview', 0, '总览', 'home', false),
          navItem('header/nav-map', 0, '地图监视', 'map-pin', false),
          navItem('header/nav-data', 0, '数据分析', 'bar-chart-3', false),
          navItem('header/nav-device', 0, '设备配对', 'cpu', true),
        ],
      ),
      rect('header/divider', 0, 117, 1586, 1, { fill: COLORS.border }),
    ],
  );

  const sidebar = frame(
    'sidebar',
    0,
    118,
    190,
    874,
    {
      fill: COLORS.panel,
    },
    [
      rect('sidebar/divider', 189, 0, 1, 874, { fill: COLORS.border }),
      navItem('sidebar/nav-overview', 14, '总览', 'home', false),
      navItem('sidebar/nav-map', 14, '地图监视', 'map-pin', false),
      navItem('sidebar/nav-data', 14, '数据分析', 'bar-chart-3', false),
      navItem('sidebar/nav-device', 14, '设备配对', 'cpu', true),
      seaweedDecoration(),
      sidebarMascot(),
    ],
  );

  const toolbar = frame(
    'toolbar',
    214,
    143,
    394,
    40,
    {
      layout: 'horizontal',
      gap: 12,
      alignItems: 'center',
    },
    [
      topButton('toolbar/add', 0, '添加设备', 'plus', 'primary', 118),
      topButton('toolbar/refresh', 0, '刷新列表', 'refresh-cw', 'secondary', 118),
      topButton('toolbar/batch', 0, '批量操作', 'chevron-down', 'secondary', 118),
    ],
  );

  const cards = frame(
    'cards',
    214,
    220,
    962,
    600,
    {
      fill: '#ffffff00',
    },
    [
      deviceCard(devices[0], 0, 0),
      deviceCard(devices[1], 326, 0),
      deviceCard(devices[2], 652, 0),
      deviceCard(devices[3], 0, 286),
      deviceCard(devices[4], 326, 286),
      deviceCard(devices[5], 652, 286),
    ],
  );

  const sortDropZone = frame(
    'sort-drop-zone',
    214,
    804,
    962,
    78,
    {
      fill: '#f9fdff',
      cornerRadius: 16,
      stroke: { thickness: 2, fill: '#0ea5e955', dashPattern: [8, 6] },
    },
    [
      iconNode('sort-drop-zone/icon', 466, 24, 20, 'move', COLORS.primary),
      textNode('sort-drop-zone/text', 368, 45, 226, 18, '拖拽设备卡片可调整顺序', {
        fontSize: 13,
        fontWeight: 700,
        fill: COLORS.muted,
        textAlign: 'center',
      }),
    ],
  );

  const rightPanel = frame(
    'right-panel',
    1218,
    141,
    344,
    741,
    {
      fill: COLORS.panel,
      cornerRadius: 18,
      stroke: { thickness: 1, fill: COLORS.border },
      effect: SHADOW_PANEL,
    },
    [
      textNode('right-panel/title', 22, 22, 140, 22, '添加新设备', {
        fontSize: 18,
        fontWeight: 800,
        fill: COLORS.text,
      }),
      textNode('right-panel/subtitle', 22, 48, 120, 16, '扫描附近设备', {
        fontSize: 12,
        fontWeight: 700,
        fill: COLORS.muted,
      }),
      radarScanner('right-panel/radar', 32, 86),
      frame(
        'right-panel/list-title-row',
        20,
        376,
        304,
        20,
        {
          layout: 'horizontal',
          justifyContent: 'space_between',
          alignItems: 'center',
        },
        [
          textNode('right-panel/list-title', 0, 0, 120, 16, '传感器对比', {
            fontSize: 14,
            fontWeight: 800,
            fill: COLORS.text,
          }),
          textNode('right-panel/list-head-right', 0, 0, 120, 16, '最新值 (单位)', {
            fontSize: 10,
            fontWeight: 700,
            fill: COLORS.muted,
            textAlign: 'right',
          }),
        ],
      ),
      frame(
        'right-panel/list-head-left',
        20,
        398,
        120,
        16,
        {},
        [
          textNode('right-panel/list-head-left-text', 0, 0, 120, 14, '藻毒素 (µg/L)', {
            fontSize: 10,
            fontWeight: 700,
            fill: COLORS.muted,
          }),
        ],
      ),
      ...comparisonRows.map((row, index) => comparisonRow(row, index)),
      frame(
        'right-panel/footer-box',
        210,
        656,
        114,
        94,
        {
          fill: '#eaf5ff',
          cornerRadius: 22,
          stroke: { thickness: 1, fill: '#8ec5ff', dashPattern: [6, 4] },
        },
        [
          iconNode('right-panel/footer-icon', 37, 18, 40, 'flask-conical', COLORS.primary),
          textNode('right-panel/footer-label', 0, 66, 114, 16, '吉祥物', {
            fontSize: 10,
            fontWeight: 700,
            fill: COLORS.primary,
            textAlign: 'center',
          }),
        ],
      ),
      frame(
        'right-panel/footer-box-2',
        168,
        682,
        84,
        84,
        {
          fill: '#eef8ff',
          cornerRadius: 22,
          stroke: { thickness: 1, fill: '#8ec5ff', dashPattern: [6, 4] },
        },
        [
          iconNode('right-panel/footer-icon-2', 25, 16, 34, 'microscope', COLORS.primary),
          textNode('right-panel/footer-label-2', 0, 58, 84, 14, '烧杯', {
            fontSize: 9,
            fontWeight: 700,
            fill: COLORS.muted,
            textAlign: 'center',
          }),
        ],
      ),
    ],
  );

  const backgroundOrbs = [
    ellipse('bg-orb-1', 1140, 18, 280, 160, {
      fill: '#ffffff88',
      opacity: 0.28,
    }),
    ellipse('bg-orb-2', 1288, 574, 180, 180, {
      fill: '#dceeff66',
      opacity: 0.4,
    }),
    ellipse('bg-orb-3', 222, 152, 120, 120, {
      fill: '#ffffff66',
      opacity: 0.42,
    }),
    ellipse('bg-orb-4', 1240, 250, 76, 76, {
      fill: '#ffffff55',
      opacity: 0.34,
    }),
    ellipse('bg-orb-5', 1460, 138, 14, 14, { fill: '#8ec5ff55' }),
    ellipse('bg-orb-6', 1502, 206, 10, 10, { fill: '#8ec5ff55' }),
    ellipse('bg-orb-7', 1450, 344, 12, 12, { fill: '#8ec5ff55' }),
    ellipse('bg-orb-8', 1498, 420, 9, 9, { fill: '#8ec5ff55' }),
    ellipse('bg-orb-9', 1476, 512, 12, 12, { fill: '#8ec5ff55' }),
  ];

  return frame(
    'device-pairing-page',
    0,
    0,
    1586,
    992,
    {
      fill: COLORS.bg,
      clip: true,
    },
    [
      ...backgroundOrbs,
      header,
      sidebar,
      toolbar,
      cards,
      sortDropZone,
      rightPanel,
      bottomDecoration(),
    ],
  );
}

return [buildPage()];
