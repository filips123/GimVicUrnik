<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Vpišite geslo
    </v-toolbar>
    <v-card-text class="text--primary mt-4">
      <p>
        Za ogled okrožnic znotraj aplikacije je potrebno geslo.
        Geslo je dostopno v <a href="https://ucilnica.gimvic.org/course/view.php?id=118" target="_blank">spletni učilnici</a>.
      </p>
    <v-text-field
        v-model="documentsPassword"
        label="Geslo"
        :append-icon="inputShow ? mdiEye : mdiEyeOff"
        :type="inputShow ? 'text' : 'password'"
        @click:append="inputShow = !inputShow"
        @keyup.enter="closeDialog()"
        autofocus
        color="green"
    />
    </v-card-text>
    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { mdiEye, mdiEyeOff } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule } from '@/store/modules/settings'
import { displaySnackbar } from '@/utils/snackbar'

@Component
export default class DocumentsPassword extends Vue {
  mdiEye = mdiEye
  mdiEyeOff = mdiEyeOff

  inputShow = false

  get documentsPassword (): string | null {
    return SettingsModule.documentsPassword
  }

  set documentsPassword (password: string | null) {
    SettingsModule.setDocumentsPassword(password || null)
  }

  closeDialog (): void {
    if (this.documentsPassword === process.env.VUE_APP_DOCUMENTS_PASSWORD) {
      displaySnackbar('Geslo je pravilno')
    } else if (this.documentsPassword) {
      displaySnackbar('Geslo je napačno')
      this.documentsPassword = ''
    }
    this.$emit('closeDialog')
  }
}
</script>
