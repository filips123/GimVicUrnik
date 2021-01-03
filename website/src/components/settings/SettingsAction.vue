<!-- Component that displays styled settings button -->

<template>
  <v-row>
    <v-col>
      <v-input :append-icon="mdiTuneVariant"
        :messages="message"
        class="settings-dialog-input"
        @click.native.stop="inputClicked = true">
        {{ label }}
      </v-input>
    </v-col>
  </v-row>
</template>

<style lang="scss">
// Make text unselectable and set pointer cursor
.settings-dialog-input {
  cursor: pointer;
  user-select: none;
}

// Align icon to the center
.settings-dialog-input .v-input__append-outer {
  margin: auto 6px;
}
</style>

<script lang="ts">
import { mdiTuneVariant } from '@mdi/js'
import { Component, ModelSync, Prop, Vue } from 'vue-property-decorator'

@Component
export default class SettingsAction extends Vue {
  mdiTuneVariant = mdiTuneVariant

  @Prop() label!: string
  @Prop() message!: string
  @ModelSync('value', 'input') inputClicked!: boolean
}
</script>
