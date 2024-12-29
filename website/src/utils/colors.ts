export enum AccentColorName {
  Red = 'red',
  Pink = 'pink',
  Purple = 'purple',
  Indigo = 'indigo',
  Blue = 'blue',
  Cyan = 'cyan',
  Teal = 'teal',
  Green = 'green',
  Lime = 'lime',
  Amber = 'amber',
  Orange = 'Orange',
  Black = 'black',
}

export interface AccentColor {
  /**
   * The name of the accent color.
   */
  name: AccentColorName

  /**
   * The primary color, used for the app and modal bars.
   */
  primary: string

  /**
   * The secondary color, used for buttons, links,
   * switches, etc. on the light theme.
   *
   * This color should be darker than the secondary dark
   * to ensure good contrast with the light background.
   */
  secondaryLight: string

  /**
   * The secondary color, used for buttons, links,
   * switches, etc. on the dark theme.
   *
   * This color should be lighter than the secondary light
   * to ensure good contrast with the dark background.
   */
  secondaryDark: string

  /**
   * The theme color, used for the PWA status bar.
   */
  theme: string

  /**
   * The current time color, used for the current time
   * indicator in the timetable on the light theme.
   */
  currentTime: string
}

/**
 * The available accent colors.
 *
 * Most colors are from the Material Design palette,
 * with some variations for better contrast and appearance.
 *
 * Make sure that colors are ordered the same as in the enum
 * and that all color codes are in lowercase letters.
 * Also, remember to add the localized name for each color
 * in the localization file.
 */
export const accentColors: AccentColor[] = [
  {
    name: AccentColorName.Red,
    primary: '#c62828', // red-darken-3
    secondaryLight: '#d32F2f', // red-darken-2
    secondaryDark: '#e57373', // red-lighten-2
    theme: '#b71c1c', // red-darken-4
    currentTime: '#e57373', // red-lighten-2
  },
  {
    name: AccentColorName.Pink,
    primary: '#ad1457', // pink-darken-3
    secondaryLight: '#c2185b', // pink-darken-2
    secondaryDark: '#f06292', // pink-lighten-2
    theme: '#880e4f', // pink-darken-4
    currentTime: '#f06292', // pink-lighten-2
  },
  {
    name: AccentColorName.Purple,
    primary: '#6a1b9a', // purple-darken-3
    secondaryLight: '#7b1fa2', // purple-darken-2
    secondaryDark: '#ba68c8', // purple-lighten-2
    theme: '#4a148c', // purple-darken-4
    currentTime: '#ba68c8', // purple-lighten-2
  },
  {
    name: AccentColorName.Indigo,
    primary: '#3f51b5', // indigo
    secondaryLight: '#303f9f', // indigo-darken-2
    secondaryDark: '#7986cb', // indigo-lighten-2
    theme: '#303f9f', // indigo-darken-2
    currentTime: '#7986cb', // indigo-lighten-2
  },
  {
    name: AccentColorName.Blue,
    primary: '#1976d2', // blue-darken-2
    secondaryLight: '#1565c0', // blue-darken-3
    secondaryDark: '#64b5f6', // blue-lighten-2
    theme: '#1565c0', // blue-darken-3
    currentTime: '#64b5f6', // blue-lighten-2
  },
  {
    name: AccentColorName.Cyan,
    primary: '#00bcd4', // cyan
    secondaryLight: '#00838f', // cyan-darken-3
    secondaryDark: '#4dd0e1', // cyan-lighten-2
    theme: '#0097a7', // cyan-darken-2
    currentTime: '#4dd0e1', // cyan-lighten-2
  },
  {
    name: AccentColorName.Teal,
    primary: '#00796b', // teal-darken-2
    secondaryLight: '#00695c', // teal-darken-3
    secondaryDark: '#4db6ac', // teal-lighten-2
    theme: '#00695c', // teal-darken-3
    currentTime: '#4db6ac', // teal-lighten-2
  },
  {
    name: AccentColorName.Green,
    primary: '#008800',
    secondaryLight: '#007700',
    secondaryDark: '#369d36',
    theme: '#007300',
    currentTime: '#369d36',
  },
  {
    name: AccentColorName.Lime,
    primary: '#cddc39', // lime
    secondaryLight: '#827717', // lime-darken-4
    secondaryDark: '#afb42b', // lime-darken-2
    theme: '#c0ca33', // lime-darken-1
    currentTime: '#cddc39', // lime
  },
  {
    name: AccentColorName.Amber,
    primary: '#ffc107', // amber
    secondaryLight: '#ff6f00', // amber-darken-4
    secondaryDark: '#ffa000', // amber-darken-2
    theme: '#ffa000', // amber-darken-2
    currentTime: '#ffc107', // amber
  },
  {
    name: AccentColorName.Orange,
    primary: '#ff9800', // orange
    secondaryLight: '#e65100', // orange-darken-4
    secondaryDark: '#f57c00', // orange-darken-2
    theme: '#f57c00', // orange-darken-2
    currentTime: '#ff9800', // orange
  },
  {
    name: AccentColorName.Black,
    primary: '#080808',
    secondaryLight: '#0d47a1', // blue-darken-4
    secondaryDark: '#64b5f6', // blue-lighten-2
    theme: '#000000',
    currentTime: '#777777',
  },
]
