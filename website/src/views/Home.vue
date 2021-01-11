<template>
  <loading />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import Loading from '@/components/base/Loading.vue'
import router from '@/router'
import { SettingsModule } from '@/store/modules/settings'
import { displaySnackbar } from '@/utils/snackbar'

@Component({
  components: { Loading }
})
export default class Home extends Vue {
  created (): void {
    let isEntitySelected: boolean

    try {
      isEntitySelected = !!SettingsModule.selectedEntity
    } catch {
      isEntitySelected = false
    }

    // Display updated message
    if ('updated' in this.$route.query) {
      displaySnackbar('Aplikacija posodobljena')
    }

    // Redirect user either to timetable or welcome page
    if (isEntitySelected) {
      router.replace({ name: 'timetable' })
    } else {
      router.replace({ name: 'welcome' })
    }
  }
}
</script>
