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
    <settings-switch v-model="showHoursInTimetable" label="Prikaži ure v urniku" />
    <settings-switch v-model="enablePullToRefresh" label="Poteg za posodobitev" />
    <settings-switch v-model="enableUpdateOnLoad" label="Samodejno posodabljanje" />

    <v-divider class="my-6" />

    <settings-action v-model="dataCollectionDialog"
      :icon="mdiDatabaseImportOutline"
      :message="dataCollectionStatus"
      label="Zbiranje tehničnih podatkov" />

    <settings-action v-model="themeSelectionDialog"
      :icon="mdiWeatherNight"
      :message="themeStatus"
      label="Barvna tema" />

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

    <v-dialog v-model="dataCollectionDialog" width="35rem">
      <data-collection-selection v-if="dataCollectionDialog" @closeDialog=closeDataCollectionDialog />
    </v-dialog>

    <v-dialog v-model="themeSelectionDialog" width="35rem">
      <theme-selection v-if="themeSelectionDialog" @closeDialog=closeThemeDialog />
    </v-dialog>
  </div>
</template>

<style lang="scss">
// Add back top padding that is removed by a dialog
.v-dialog > .v-card > .v-card__text {
  padding: 16px 24px 20px !important;
}

// Center settings page
.settings {
  margin: 0 auto;
  max-width: 40rem;
}
</style>

<script lang="ts">
import { mdiDatabaseImportOutline, mdiTuneVariant, mdiUpdate, mdiWeatherNight } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

import DataCollectionSelection from '@/components/settings/DataCollectionSelection.vue'
import EntitySelection from '@/components/settings/EntitySelection.vue'
import SettingsAction from '@/components/settings/SettingsAction.vue'
import SettingsSwitch from '@/components/settings/SettingsSwitch.vue'
import ThemeSelection from '@/components/settings/ThemeSelection.vue'
import { EntityType, LunchType, SettingsModule, SnackType, ThemeType } from '@/store/modules/settings'
import { StorageModule, updateAllData } from '@/store/modules/storage'

@Component({
  components: { DataCollectionSelection, ThemeSelection, SettingsAction, SettingsSwitch, EntitySelection }
})
export default class Settings extends Vue {
  mdiTuneVariant = mdiTuneVariant
  mdiDatabaseImportOutline = mdiDatabaseImportOutline
  mdiWeatherNight = mdiWeatherNight
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

  // Get data collection status as string from storage
  get dataCollectionStatus (): string {
    if (SettingsModule.dataCollection.performance && SettingsModule.dataCollection.crashes) {
      return 'Merjenje učinkovitosti & Zbiranje napak'
    } else if (SettingsModule.dataCollection.performance) {
      return 'Merjenje učinkovitosti'
    } else if (SettingsModule.dataCollection.crashes) {
      return 'Zbiranje napak'
    } else {
      return 'Izklopljeno'
    }
  }

  // Get theme type as string from enum
  get themeStatus (): string {
    switch (SettingsModule.theme) {
      case ThemeType.System:
        return 'Sistemska'
      case ThemeType.Light:
        return 'Svetla'
      case ThemeType.Dark:
        return 'Temna'
    }
  }

  // Dialog states
  entitySelectionDialog = false
  snackSelectionDialog = false
  lunchSelectionDialog = false
  dataCollectionDialog = false
  themeSelectionDialog = false

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

  get showHoursInTimetable (): boolean {
    return SettingsModule.showHoursInTimetable
  }

  set showHoursInTimetable (showHoursInTimetable: boolean) {
    SettingsModule.setShowHoursInTimetable(showHoursInTimetable)
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

  // Prepare view
  created (): void {
    document.title = process.env.VUE_APP_TITLE + ' – Nastavitve'
    this.$emit('setPageTitle', process.env.VUE_APP_SHORT + ' – Nastavitve')

    this.$emit('setPullToRefreshAllowed', false)
  }

  destroyed (): void {
    this.$emit('setPullToRefreshAllowed', true)
  }

  // Handle update requests
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

  // Handle dialogs
  closeEntityDialog (): void {
    this.entitySelectionDialog = false
  }

  closeSnackDialog (): void {
    this.snackSelectionDialog = false
  }

  closeLunchDialog (): void {
    this.lunchSelectionDialog = false
  }

  closeDataCollectionDialog (): void {
    this.dataCollectionDialog = false
  }

  closeThemeDialog (): void {
    this.themeSelectionDialog = false
  }
}
</script>
