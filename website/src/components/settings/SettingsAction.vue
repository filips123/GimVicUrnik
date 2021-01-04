<!-- Component that displays styled settings button -->

<template>
  <v-row>
    <v-col>
      <v-input :append-icon="icon"
        :messages="message"
        class="settings-dialog-input"
        @click.native="inputClicked = true">
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
import { Component, ModelSync, Prop, Vue } from 'vue-property-decorator'

@Component
export default class SettingsAction extends Vue {
  @Prop() icon!: string
  @Prop() label!: string
  @Prop() message!: string
  @ModelSync('value', 'input') inputClicked!: boolean
}
</script>
