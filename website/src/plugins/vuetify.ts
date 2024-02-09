import 'vuetify/styles'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import '@mdi/font/css/materialdesignicons.css'
import {
  VApp,
  VAppBar,
  VAppBarTitle,
  VBottomNavigation,
  VBtn,
  VCard,
  VCardActions,
  VCardText,
  VCheckbox,
  VCol,
  VContainer,
  VDialog,
  VDivider,
  VExpansionPanel,
  VExpansionPanels,
  VExpansionPanelText,
  VInput,
  VList,
  VListItem,
  VMain,
  VNavigationDrawer,
  VRadio,
  VRadioGroup,
  VRow,
  VSnackbar,
  VSwitch,
  VTab,
  VTable,
  VTabs,
  VTextField,
  VVirtualScroll,
} from 'vuetify/components'
import { Touch } from 'vuetify/directives'

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
  },
}

const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
  },
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
      darkTheme,
    },
  },
  aliases: {
    VDividerBiggerMargin: VDivider,
    VListItemSwitch: VListItem,
    VBtnIcon: VBtn,
    VBtnSubscribe: VBtn,
    VCardTextSelection: VCardText,
  },
  defaults: {
    // Aliases
    VDividerBiggerMargin: {
      class: 'my-6',
    },
    VListItemSwitch: {
      class: 'pa-0 my-1',
    },
    VBtnIcon: {
      color: 'inherit',
      variant: 'text',
    },
    VBtnSubscribe: {
      class: 'text-primary-variant pa-0',
      variant: 'text',
    },
    VCardTextSelection: {
      class: 'pa-0',
    },

    // Defaults
    VAppBar: {
      color: 'primary',
    },
    VSwitch: {
      color: 'primary-variant',
    },
    VTextField: {
      color: 'primary-variant',
    },
    VListItem: {
      class: 'text-text',
    },
    VExpansionPanel: {
      class: 'text-text',
    },
    VBottomNavigation: {
      class: 'bg-navigation',
    },
    VNavigationDrawer: {
      class: 'bg-navigation',
    },
    VTable: {
      class: 'text-text elevation-2',
    },
    VContainer: {
      class: 'px-4 pt-4 pb-2',
    },
    VCard: {
      class: 'text-text mx-2 mb-2',
      style: 'white-space: pre-line;',
    },
    VExpansionPanels: {
      style: 'margin: 16px auto; max-width: 40rem;',
    },
    VExpansionPanelTitle: {
      style: 'line-height: 1rem; min-height: 48px; padding: 0 16px;',
    },
    VSnackbar: {
      style: 'margin-bottom: 60px; min-width: 200px;',
    },
    VDialog: {
      width: '25rem',
      scrollable: true,
      VCard: {
        style: 'box-shadow: none',
      },
      VCardItem: {
        class: 'bg-primary pa-3',
      },
      VCardTitle: {
        class: 'text-uppercase',
        style: 'white-space: normal;',
      },
      VCardSubtitle: {
        style: 'white-space: normal;',
      },
      VCardText: {
        class: 'pa-4',
      },
      VCardActions: {
        class: 'justify-end bg-surface-variation',
      },
      VCheckbox: {
        color: 'primary-variant',
        class: 'pa-0',
      },
      VCheckboxBtn: {
        style: '--v-input-control-height: 0px;',
      },
      VBtn: {
        class: 'text-primary-variant',
        variant: 'text',
      },
      VRadioGroup: {
        color: 'primary-variant',
        class: 'pa-0',
      },
      VDivider: {
        class: 'my-3',
      },
    },
  },
  components: {
    VApp,
    VAppBar,
    VAppBarTitle,
    VBottomNavigation,
    VBtn,
    VCard,
    VCardActions,
    VCardText,
    VCheckbox,
    VCol,
    VContainer,
    VDialog,
    VDivider,
    VExpansionPanel,
    VExpansionPanels,
    VExpansionPanelText,
    VInput,
    VList,
    VListItem,
    VMain,
    VNavigationDrawer,
    VRadio,
    VRadioGroup,
    VRow,
    VSnackbar,
    VSwitch,
    VTab,
    VTable,
    VTabs,
    VTextField,
    VVirtualScroll,
  },
  directives: {
    Touch,
  },
})

export default vuetify
