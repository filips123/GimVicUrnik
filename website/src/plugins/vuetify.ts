import 'vuetify/styles'

import type { ThemeDefinition } from 'vuetify'
import { createVuetify } from 'vuetify'
import { VBtn, VCardText, VDivider, VListItem, VSheet } from 'vuetify/components'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

const lightTheme: ThemeDefinition = {
  dark: false,
  colors: {
    primary: '#369d36',
    'primary-variant': '#009300',
    background: '#ffffff',
    text: '#000000',
    navigation: '#ffffff',
    surface: '#ffffff',
    'surface-variation': '#f6f6f6',
    'surface-variation-secundary': '#eeeeee',
    'on-surface': '#121212',
    'current-time': '#369d36',
  },
  variables: {
    'disabled-opacity': 0.2,
    'current-time-opacity': 0.1,
  },
}

const darkTheme: ThemeDefinition = {
  dark: true,
  colors: {
    primary: '#009300',
    'primary-variant': '#369d36',
    background: '#121212',
    text: '#ffffff',
    navigation: '#363636',
    surface: '#1e1e1e',
    'surface-variation': '#222222',
    'surface-variation-secundary': '#303030',
    'on-surface': '#121212',
    'current-time': '#121212',
  },
  variables: {
    'disabled-opacity': 0.2,
    'current-time-opacity': 0.7,
  },
}

const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },

  // TODO: Check themes
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
      darkTheme,
    },
  },

  // TODO: Is this used anywhere?
  locale: {
    locale: 'sl',
  },

  aliases: {
    VDividerSettings: VDivider,
    VListItemSwitch: VListItem,
    VBtnIcon: VBtn,
    VBtnSubscribe: VBtn,
    VCardTextSelection: VCardText,
    VColumn: VSheet,
  },

  // TODO: Check these styles and aliases

  defaults: {
    // Aliases

    // VDividerSettings: {
    //   class: 'my-6',
    // },
    // VListItemSwitch: {
    //   class: 'pa-0 my-1',
    // },
    VBtnIcon: {
      color: 'inherit',
      variant: 'text',
    },
    // VBtnSubscribe: {
    //   class: 'text-primary-variant pa-0',
    //   variant: 'text',
    // },
    // VCardTextSelection: {
    //   class: 'pa-0',
    // },
    VColumn: {
      class: 'bg-background mx-auto',
      style: 'max-width: 35rem;',
    },

    // Defaults

    // VAppBar: {
    //   color: 'primary',
    // },
    // VSwitch: {
    //   color: 'primary-variant',
    // },
    // VTextField: {
    //   color: 'primary-variant',
    //   class: 'text-uppercase',
    // },
    // VListItem: {
    //   class: 'text-text',
    // },
    // VExpansionPanel: {
    //   class: 'text-text',
    // },
    // VBottomNavigation: {
    //   class: 'bg-navigation',
    // },
    // VNavigationDrawer: {
    //   class: 'bg-navigation',
    // },
    // VTable: {
    //   class: 'text-text elevation-2',
    // },
    // VContainer: {
    //   class: 'px-4 pt-4 pb-2',
    // },
    // VCard: {
    //   class: 'text-text mx-2 mb-2',
    //   style: 'white-space: pre-line;',
    // },
    // VExpansionPanels: {
    //   style: 'margin: 16px auto; max-width: 40rem;',
    // },
    // VExpansionPanelTitle: {
    //   style: 'line-height: 1rem; min-height: 48px; padding: 0 16px;',
    // },
    // VSnackbar: {
    //   style: 'margin-bottom: 60px; min-width: 200px;',
    // },
    VDialog: {
      width: '50rem',
      scrollable: true,
      // VCard: {
      //   class: 'elevation-10 text-text',
      // },
      // VCardItem: {
      //   class: 'bg-primary pa-3',
      // },
      // VCardTitle: {
      //   class: 'text-uppercase',
      //   style: 'white-space: normal;',
      // },
      // VCardSubtitle: {
      //   style: 'white-space: normal;',
      // },
      // VCardText: {
      //   class: 'pa-4',
      // },
      // VCardActions: {
      //   class: 'justify-end bg-surface-variation',
      // },
      // VCheckbox: {
      //   color: 'primary-variant',
      //   class: 'pa-0',
      // },
      // VCheckboxBtn: {
      //   style: '--v-input-control-height: 0px;',
      // },
      // VBtn: {
      //   class: 'text-primary-variant',
      //   variant: 'text',
      // },
      // VRadioGroup: {
      //   color: 'primary-variant',
      //   class: 'pa-0',
      // },
      // VDivider: {
      //   class: 'my-3',
      // },
    },
  },
})

export default vuetify
