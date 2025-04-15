import 'vuetify/styles'

import type { ThemeDefinition } from 'vuetify'
import { createVuetify } from 'vuetify'
import { VBtn, VCard, VDivider, VSheet, VTable } from 'vuetify/components'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'
import { sl } from 'vuetify/locale'

import { AccentColorName, accentColors } from '@/utils/colors'

const accentColor = accentColors.find(color => color.name === AccentColorName.Black)!

const lightTheme: ThemeDefinition = {
  dark: false,
  colors: {
    primary: accentColor.primary,
    secondary: accentColor.secondaryLight,
    'surface-subtle': '#f6f6f6',
    'surface-medium': '#e6e6e6',
    'surface-highlighted': '#efefef',
  },
  variables: {
    'app-subtitle-opacity': 0.8,
    'card-subtitle-opacity': 0.8,
    'current-time-color': accentColor.currentTime,
    'current-time-opacity': 0.1,
    'overlay-color': '#000000',
    'overlay-opacity': 0.42,
  },
}

const darkTheme: ThemeDefinition = {
  dark: true,
  colors: {
    primary: accentColor.primary,
    secondary: accentColor.secondaryDark,
    'surface-subtle': '#1c1c1c',
    'surface-medium': '#262626',
    'surface-highlighted': '#2c2c2c',
  },
  variables: {
    'app-subtitle-opacity': 0.8,
    'card-subtitle-opacity': 0.8,
    'current-time-color': '#000000',
    'current-time-opacity': 0.31,
    'overlay-color': '#121212',
    'overlay-opacity': 0.48,
  },
}

const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },

  theme: {
    defaultTheme: 'light',
    themes: {
      light: lightTheme,
      dark: darkTheme,
    },
  },

  display: {
    mobileBreakpoint: 1174,
  },

  locale: {
    locale: 'sl',
    messages: { sl },
  },

  aliases: {
    VDividerSettings: VDivider,
    VBtnIcon: VBtn,
    VBtnSubscribe: VBtn,
    VColumn: VSheet,
    VTableMain: VTable,
    VCardMain: VCard,
  },

  defaults: {
    // Global

    global: {
      hideDetails: 'auto',
    },

    // Aliases

    VDividerSettings: {
      class: 'my-6',
    },
    VBtnIcon: {
      color: 'inherit',
      variant: 'text',
    },
    VBtnSubscribe: {
      color: 'secondary',
      class: 'px-1 ms-n1 me-2',
      variant: 'text',
    },
    VColumn: {
      class: 'bg-background mx-auto',
      style: 'max-width: 35rem;',
    },
    VTableMain: {
      class: 'elevation-light rounded',
    },
    VCardMain: {
      class: 'elevation-light rounded mb-2 text-pre-line',
    },

    // Defaults

    VAppBar: {
      color: 'primary',
    },
    VSwitch: {
      color: 'secondary',
    },
    VCheckbox: {
      color: 'secondary',
    },
    VRadioGroup: {
      color: 'secondary',
    },
    VTextField: {
      color: 'secondary',
    },
    VDialog: {
      width: '50rem',
      scrollable: true,
      VCardItem: {
        class: 'bg-primary pa-3',
      },
      VCardTitle: {
        class: 'text-wrap',
        style: 'font-size: 1.15rem;',
      },
      VCardSubtitle: {
        class: 'text-wrap',
      },
      VCardText: {
        class: 'pa-4',
      },
      VCardActions: {
        class: 'justify-end bg-surface-subtle',
      },
      VCheckbox: {
        class: 'pa-0',
      },
      VCheckboxBtn: {
        style: '--v-input-control-height: 0px;',
      },
      VRadioGroup: {
        class: 'pa-0',
      },
      VBtn: {
        color: 'secondary',
        variant: 'text',
      },
    },
  },
})

export default vuetify
