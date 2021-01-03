<!-- Component that displays styled settings toggle -->

<template>
  <v-row>
    <v-col>
      <v-switch v-model="isChecked" class="v-input--reverse" color="green">
        <template v-slot:label>
          <span class="text-body-1 text--primary">
            {{ label }}
          </span>
        </template>
      </v-switch>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, ModelSync, Prop, Vue } from 'vue-property-decorator'

@Component
export default class SettingsSwitch extends Vue {
  @Prop() label!: string
  @ModelSync('value', 'input') isChecked!: boolean
}
</script>
