<template>
  <v-row class="ma-3 pt-8" justify="center">
    <entity-selection initial-selection-stage="0" />
  </v-row>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import EntitySelection from '@/components/settings/EntitySelection.vue'

@Component({
  components: { EntitySelection }
})
export default class Welcome extends Vue {
  created (): void {
    document.title = process.env.VUE_APP_TITLE
    this.$emit('setPageTitle', process.env.VUE_APP_TITLE)

    this.$emit('setPullToRefreshAllowed', false)
    this.$emit('setNavigationDisplay', false)
  }

  destroyed (): void {
    this.$emit('setPullToRefreshAllowed', true)
    this.$emit('setNavigationDisplay', true)
  }
}
</script>
