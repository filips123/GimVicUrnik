<template>
  <div class="settings px-4 pt-4">
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
    <settings-switch v-model="enableShowingDetails" label="Klikni za podrobnosti" />
    <settings-switch v-model="enablePullToRefresh" label="Potegni za posodobitev" />
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

    <settings-action v-model="moodleTokenDialog"
      :icon="mdiKey"
      :message="moodleTokenStatus"
      label="Moodle žeton" />

    <v-divider class="my-6" />

    <settings-action :icon="mdiUpdate"
      :message="`Trenutna različica: ${appVersion}`"
      label="Posodobi aplikacijo"
      @click.native="updateApp" />

    <settings-action :icon="mdiUpdate"
      :message="`Trenutna različica: ${dataVersion}`"
      label="Posodobi podatke"
      @click.native="updateData" />

    <v-divider class="my-6" />

    <settings-action v-model="aboutDialog"
      :icon="mdiInformationOutline"
      :message="`Trenutna različica: ${appVersion}`"
      label="O aplikaciji" />

    <v-dialog v-model="entitySelectionDialog"
      v-bind:persistent="entitySelectionPersistent"
      content-class="settings-dialog"
      width="35rem">
      <entity-selection v-if="entitySelectionDialog"
        initial-selection-stage="1"
        is-dialog="1"
        @closeDialog=closeEntityDialog
        @persistDialog=persistEntityDialog />
    </v-dialog>

    <v-dialog v-model="snackSelectionDialog" content-class="settings-dialog" width="35rem">
      <snack-selection v-if="snackSelectionDialog" @closeDialog=closeSnackDialog />
    </v-dialog>

    <v-dialog v-model="lunchSelectionDialog" content-class="settings-dialog" width="35rem">
      <lunch-selection v-if="lunchSelectionDialog" @closeDialog=closeLunchDialog />
    </v-dialog>

    <v-dialog v-model="dataCollectionDialog" content-class="settings-dialog" width="35rem">
      <data-collection-selection v-if="dataCollectionDialog" @closeDialog=closeDataCollectionDialog />
    </v-dialog>

    <v-dialog v-model="themeSelectionDialog" content-class="settings-dialog" width="35rem">
      <theme-selection v-if="themeSelectionDialog" @closeDialog=closeThemeDialog />
    </v-dialog>

    <v-dialog v-model="moodleTokenDialog" content-class="settings-dialog" width="35rem">
      <moodle-token v-if="moodleTokenDialog" @closeDialog=closeMoodleTokenDialog />
    </v-dialog>

    <v-dialog v-model="aboutDialog" content-class="settings-dialog" width="35rem">
      <about v-if="aboutDialog" @closeDialog=closeAboutDialog />
    </v-dialog>
  </div>
</template>

<style lang="scss">
// Add back top padding that is removed by a dialog
.settings-dialog.v-dialog > .v-card > .v-card__text {
  padding: 16px 24px 20px !important;
}

// Center settings page
.settings {
  margin: 0 auto;
  max-width: 40rem;
}
</style>

<script lang="ts">
import { mdiDatabaseImportOutline, mdiInformationOutline, mdiKey, mdiTuneVariant, mdiUpdate, mdiWeatherNight } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

import About from '@/components/settings/About.vue'
import DataCollectionSelection from '@/components/settings/DataCollectionSelection.vue'
import EntitySelection from '@/components/settings/EntitySelection.vue'
import LunchSelection from '@/components/settings/LunchSelection.vue'
import MoodleToken from '@/components/settings/MoodleToken.vue'
import SettingsAction from '@/components/settings/SettingsAction.vue'
import SettingsSwitch from '@/components/settings/SettingsSwitch.vue'
import SnackSelection from '@/components/settings/SnackSelection.vue'
import ThemeSelection from '@/components/settings/ThemeSelection.vue'
import { EntityType, LunchType, SettingsModule, SnackType, ThemeType } from '@/store/modules/settings'
import { StorageModule, updateAllData } from '@/store/modules/storage'

@Component({
  components: {
    About,
    MoodleToken,
    DataCollectionSelection,
    ThemeSelection,
    SnackSelection,
    SettingsAction,
    SettingsSwitch,
    LunchSelection,
    EntitySelection
  }
})
export default class Settings extends Vue {
  mdiTuneVariant = mdiTuneVariant
  mdiDatabaseImportOutline = mdiDatabaseImportOutline
  mdiWeatherNight = mdiWeatherNight
  mdiUpdate = mdiUpdate
  mdiKey = mdiKey
  mdiInformationOutline = mdiInformationOutline

  // Get app version
  get appVersion (): string {
    return process.env.VUE_APP_VERSION || 'Ni podatkov'
  }

  // Get data version
  get dataVersion (): string {
    if (!StorageModule.lastUpdated) return 'Ni podatkov'

    // Date is converted to string when stored to local storage, so we need to convert it back
    const lastUpdated = typeof StorageModule.lastUpdated === 'string' ? new Date(StorageModule.lastUpdated) : StorageModule.lastUpdated
    return lastUpdated.toLocaleDateString('sl', { hour: 'numeric', minute: 'numeric' })
  }

  // Get label for entity switch
  get selectedEntityLabel (): string {
    switch (SettingsModule.selectedEntity?.type) {
      case EntityType.Teacher:
        return 'Izbran profesor'
      case EntityType.Classroom:
        return 'Izbrana učilnica'
      default:
        return 'Izbran razred'
    }
  }

  // Get currently selected entity
  get selectedEntity (): string {
    return SettingsModule.selectedEntity?.data.join(', ') || 'Razred ni izbran'
  }

  // Get snack type as string from enum
  get selectedSnack (): string {
    switch (SettingsModule.selectedMenu?.snack) {
      case SnackType.Vegetarian:
        return 'Vegetarijanska'
      case SnackType.Poultry:
        return 'Vegetarijanska s perutnino in ribo'
      case SnackType.Fruitvegetable:
        return 'Sadnozelenjavna'
      default:
        return 'Navadna'
    }
  }

  // Get lunch type as string from enum
  get selectedLunch (): string {
    switch (SettingsModule.selectedMenu?.lunch) {
      case LunchType.Vegetarian:
        return 'Vegetarijansko'
      default:
        return 'Navadno'
    }
  }

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

  // Get Moodle token status as string
  get moodleTokenStatus (): string {
    return SettingsModule.moodleToken ? 'Nastavljen' : 'Ni nastavljen'
  }

  // Dialog states
  entitySelectionDialog = false
  snackSelectionDialog = false
  lunchSelectionDialog = false
  dataCollectionDialog = false
  themeSelectionDialog = false
  moodleTokenDialog = false
  aboutDialog = false

  entitySelectionPersistent = false

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

  get enableShowingDetails (): boolean {
    return SettingsModule.enableShowingDetails
  }

  set enableShowingDetails (enableShowingDetails: boolean) {
    SettingsModule.setEnableShowingDetails(enableShowingDetails)
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
    this.$emit('setPageTitle', 'Nastavitve')

    this.$emit('setDayMenuDisplay', false)
    this.$emit('setPullToRefreshAllowed', false)
  }

  destroyed (): void {
    this.$emit('setPullToRefreshAllowed', true)
  }

  // Handle update requests
  async updateApp (): Promise<void> {
    if (process.env.NODE_ENV === 'production' && navigator.serviceWorker && navigator.serviceWorker.controller) {
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

  closeMoodleTokenDialog (): void {
    this.moodleTokenDialog = false
  }

  closeAboutDialog (): void {
    this.aboutDialog = false
  }

  persistEntityDialog (persistent: boolean): void {
    this.entitySelectionPersistent = persistent
  }
}
</script>
