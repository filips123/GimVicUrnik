<template>
  <div class="settings px-8 pt-8">
    <settings-action v-model="entitySelectionDialog"
      :icon="mdiTuneVariant"
      :label="selectedEntityLabel"
      :message="selectedEntity" />

    <settings-action v-model="snackSelectionDialog"
      :icon="mdiTuneVariant"
      :message="selectedSnack"
      label="Izbrana malica" />

    <settings-action v-model="lunchSelectionDialog"
      :icon="mdiTuneVariant"
      :message="selectedLunch"
      label="Izbrano kosilo" />

    <v-divider class="mt-6" />

    <settings-switch v-model="showSubstitutions" label="Prikaži nadomeščanja" />
    <settings-switch v-model="showLinksInTimetable" label="Prikaži povezave v urniku" />
    <settings-switch v-model="enablePullToRefresh" label="Poteg za posodobitev" />
    <settings-switch v-model="enableUpdateOnLoad" label="Samodejno posodabljanje" />

    <!-- TODO: Use three values: Default (system), light, dark -->
    <settings-switch v-model="darkTheme" label="Temni način" />

    <v-divider class="my-6" />

    <settings-action :icon="mdiUpdate"
      :message="`Trenutna različica: ${appVersion}`"
      label="Posodobi aplikacijo"
      @click.native="updateApp" />

    <settings-action :icon="mdiUpdate"
      :message="`Trenutna različica: ${dataVersion}`"
      label="Posodobi podatke"
      @click.native="updateData" />

    <!-- TODO: Add dialogs for snack and lunch selection -->

    <v-dialog v-model="entitySelectionDialog" width="35rem">
      <entity-selection v-if="entitySelectionDialog"
        initial-selection-stage="1"
        is-dialog="1"
        @closeDialog=closeEntityDialog />
    </v-dialog>
  </div>
</template>

<style lang="scss">
// Add back top padding that is removed by a dialog
.v-dialog > .v-card > .v-card__text {
  padding: 16px 24px 20px;
}

// Center settings page
.settings {
  margin: 0 auto;
  max-width: 40rem;
}
</style>

<script lang="ts">
import { mdiTuneVariant, mdiUpdate } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

import EntitySelection from '@/components/settings/EntitySelection.vue'
import SettingsAction from '@/components/settings/SettingsAction.vue'
import SettingsSwitch from '@/components/settings/SettingsSwitch.vue'
import { EntityType, LunchType, SettingsModule, SnackType } from '@/store/modules/settings'
import { StorageModule, updateAllData } from '@/store/modules/storage'

@Component({
  components: { SettingsAction, SettingsSwitch, EntitySelection }
})
export default class Settings extends Vue {
  mdiTuneVariant = mdiTuneVariant
  mdiUpdate = mdiUpdate

  // Get app version
  appVersion = process.env.VUE_APP_VERSION || 'Ni podatkov'

  // Get data version
  get dataVersion (): string {
    if (!StorageModule.lastUpdated) return 'Ni podatkov'

    const lastUpdated = typeof StorageModule.lastUpdated === 'string' ? new Date(StorageModule.lastUpdated) : StorageModule.lastUpdated
    return lastUpdated.toLocaleDateString('sl', { hour: 'numeric', minute: 'numeric' })
  }

  // Get label for entity switch
  selectedEntityLabel = (() => {
    switch (SettingsModule.selectedEntity?.type) {
      case EntityType.Class:
        return 'Izbran razred'
      case EntityType.Teacher:
        return 'Izbran profesor'
      case EntityType.Classroom:
        return 'Izbrana učilnica'
      default:
        return 'Izbran razred'
    }
  })()

  // Get currently selected entity
  selectedEntity = SettingsModule.selectedEntity?.data.join(', ') || 'Razred ni izbran'

  // Get snack type as string from enum
  selectedSnack = (() => {
    switch (SettingsModule.selectedMenu?.snack) {
      case SnackType.Normal:
        return 'Navadna'
      case SnackType.Vegetarian:
        return 'Vegetarijanska'
      case SnackType.Poultry:
        return 'Vegetarijanska s perutnino in ribo'
      case SnackType.Fruitvegetable:
        return 'Sadnozelenjavna'
      default:
        return 'Navadna'
    }
  })()

  // Get lunch type as string from enum
  selectedLunch = (() => {
    switch (SettingsModule.selectedMenu?.lunch) {
      case LunchType.Normal:
        return 'Navadno'
      case LunchType.Vegetarian:
        return 'Vegetarijansko'
      default:
        return 'Navadno'
    }
  })()

  // Dialog states
  entitySelectionDialog = false
  snackSelectionDialog = false
  lunchSelectionDialog = false

  // Sync toggles with Vuex state
  get showSubstitutions (): boolean {
    return SettingsModule.showSubstitutions
  }

  set showSubstitutions (showSubstitutions: boolean) {
    SettingsModule.setShowSubstitutions(showSubstitutions)
  }

  get showLinksInTimetable (): boolean {
    return SettingsModule.showLinksInTimetable
  }

  set showLinksInTimetable (showLinksInTimetable: boolean) {
    SettingsModule.setShowLinksInTimetable(showLinksInTimetable)
  }

  get enablePullToRefresh (): boolean {
    return SettingsModule.enablePullToRefresh
  }

  set enablePullToRefresh (enablePullToRefresh: boolean) {
    SettingsModule.setEnablePullToRefresh(enablePullToRefresh)
  }

  get enableUpdateOnLoad (): boolean {
    return SettingsModule.enableUpdateOnLoad
  }

  set enableUpdateOnLoad (enableUpdateOnLoad: boolean) {
    SettingsModule.setEnableUpdateOnLoad(enableUpdateOnLoad)
  }

  get darkTheme (): boolean {
    return SettingsModule.darkTheme || false
  }

  set darkTheme (darkTheme: boolean) {
    SettingsModule.setDarkTheme(darkTheme)
  }

  created (): void {
    document.title = process.env.VUE_APP_TITLE + ' – Nastavitve'
    this.$emit('setPageTitle', process.env.VUE_APP_SHORT + ' – Nastavitve')

    this.$emit('setPullToRefreshAllowed', false)
  }

  destroyed (): void {
    this.$emit('setPullToRefreshAllowed', true)
  }

  async updateApp (): Promise<void> {
    if (process.env.NODE_ENV === 'production' && navigator.serviceWorker.controller) {
      // Skip service worker waiting
      navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' })
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    // Add GET parameter to invalidate cache of index HTML file
    window.location.href = location.protocol + '//' + location.host + '?updated=' + (new Date()).getTime()
  }

  async updateData (): Promise<void> {
    await updateAllData()
  }

  closeEntityDialog (): void {
    this.entitySelectionDialog = false
  }

  closeSnackDialog (): void {
    this.snackSelectionDialog = false
  }

  closeLunchDialog (): void {
    this.lunchSelectionDialog = false
  }
}
</script>
