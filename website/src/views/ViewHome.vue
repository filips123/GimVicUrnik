<script setup lang="ts">
import { useRouter } from 'vue-router'

import { EntityType, useSettingsStore } from '@/stores/settings'

const router = useRouter()
const { entityType } = useSettingsStore()

// Display the app updated popup
// TODO

// Redirect the user either to timetable or welcome page
if (entityType === EntityType.None) router.replace({ name: 'welcome' })
else router.replace({ name: 'timetable' })
</script>
