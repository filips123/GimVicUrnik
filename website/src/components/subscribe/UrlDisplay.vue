<!-- Component that displays styled URL with buttons to copy and open it -->

<template>
  <div>
    <v-row class="pt-2 px-3">
      <h3 class="text-h6">{{ label }}</h3>
    </v-row>

    <v-row class="pb-2 px-3">
      <v-text-field dense
        readonly
        class="url-display-input"
        ref="input"
        color="green"
        :value="value"
        @click="autoSelect"></v-text-field>
      <div class="url-display-buttons">
        <v-btn text class="ml-n1 ml-sm-0 mr-1 pa-1" color="green" @click="copyLink">Kopiraj</v-btn>
        <v-btn text class="pa-1" color="green" @click="openLink">Odpri</v-btn>
      </div>
    </v-row>
  </div>
</template>

<style lang="scss">
.url-display-input .v-label--active {
  font-size: 1.3rem !important;
}

.url-display-input {
  padding-right: 30px;
}

@media only screen and (max-width: 390px) {
  .url-display-input {
    padding-right: 0;
  }
}

@media only screen and (max-width: 429px) {
  .url-display-buttons {
    padding-bottom: 4px;
  }
}
</style>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class UrlDisplay extends Vue {
  @Prop() label!: string
  @Prop() value!: string

  autoSelect (event: Event): void {
    const input = event.target as HTMLInputElement
    input?.focus()
    input?.select()
  }

  copyLink (): void {
    if ('clipboard' in navigator) {
      navigator.clipboard.writeText(this.value)
    } else {
      const input = ((this.$refs.input as Vue).$el as HTMLElement).querySelector('input')
      input?.focus()
      input?.select()
      document.execCommand('copy')
    }
  }

  openLink (): void {
    window.open(this.value, '_blank')
  }
}
</script>
