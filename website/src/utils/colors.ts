export enum AccentColorName {
  red = 'red',
  orange = 'orange',
  green = 'green',
  blue = 'blue',
  purple = 'purple',
  pink = 'pink',
  black = 'black',
}

export type AccentColor = {
  name: AccentColorName
  primary: string
  secondary: string
  theme: string
  currentTime: string
}

/**
 * Colors were sourced from Material colors:
 * Primary: color,
 * Secondary: color-lighten-1,
 * Theme: color-darken-1,
 * CurrentTime: color-lighten-2
 */
export const ACCENT_COLORS: AccentColor[] = [
  {
    name: AccentColorName.red,
    primary: '#F44336',
    secondary: '#EF5350',
    theme: '#E53935',
    currentTime: '#E57373',
  },
  {
    name: AccentColorName.orange,
    primary: '#FF5722',
    secondary: '#FF7043',
    theme: '#F4511E',
    currentTime: '#FF8A65',
  },
  {
    name: AccentColorName.green,
    primary: '#4CAF50',
    secondary: '#66BB6A',
    theme: '#43A047',
    currentTime: '#81C784',
  },
  {
    name: AccentColorName.blue,
    primary: '#2196F3',
    secondary: '#42A5F5',
    theme: '#1E88E5',
    currentTime: '#64B5F6',
  },
  {
    name: AccentColorName.purple,
    primary: '#9C27B0',
    secondary: '#AB47BC',
    theme: '#8E24AA',
    currentTime: '#BA68C8',
  },
  {
    name: AccentColorName.pink,
    primary: '#E91E63',
    secondary: '#EC407A',
    theme: '#D81B60',
    currentTime: '#F06292',
  },
  {
    name: AccentColorName.black,
    primary: '#000000',
    secondary: '#0D47A1',
    theme: '#000000',
    currentTime: '#64B5F6',
  },
]
