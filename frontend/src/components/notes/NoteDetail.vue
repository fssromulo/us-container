<template>
  <div v-if="computedOrder">
    <div
      v-if="props.showTitle"
      class="mb-8 text-xl font-medium border-b text-900 dark:text-0"
    >
      Notes for order {{ computedOrder.display_order_id }}
    </div>
    <div class="text-2xl">
      Created by {{ computedOrder.user.first_name }}
      {{ computedOrder.user.last_name }} on {{ dfc(computedOrder.created_at) }}
    </div>
    <ul class="p-0 m-0 list-none">
      <li class="pb-4 mb-2 border border-b" v-for="note in computedOrder.note">
        <!-- <div class="mb-2 font-medium text-900 dark:text-0">{{ note.title }}</div> -->
        <div
          class="mb-2 leading-normal text-900 dark:text-0"
          style="max-width: 30rem"
        >
          Created at {{ dfl(note.created_at) }} by {{ note.author.full_name }}
        </div>
        <div
          class="leading-normal text-800 dark:text-50"
          style="max-width: 30rem"
        >
          {{ note.content }}
        </div>
        <div
          v-if="usersStore.cms?.has_public_notes"
          class="leading-normal text-800 dark:text-50"
          style="max-width: 30rem"
        >
          Public:
          <Checkbox
            v-model="state.notes_public[note.id]"
            @change="handleCheckChanged(note.id)"
            inputId="binary"
            :binary="true"
          />
        </div>
      </li>
    </ul>
    <div
      v-if="state.showEditNote || computedOrder.note.length === 0"
      class="grid grid-cols-12 gap-4 mt-4 formgrid p-fluid"
    >
      <div class="col-span-12 mb-4 md:col-span-12">
        <p class="text-2xl">New Note</p>
      </div>
      <div class="col-span-12 mb-4 field md:col-span-6">
        <label for="street_address" class="text-sm text-700 dark:text-100"
          >Content</label
        >
        <Textarea
          v-model="state.note.content"
          :autoResize="true"
          class="p-component p-inputtext-fluid"
          rows="5"
          cols="30"
        />
      </div>
    </div>
    <div class="flex justify-between pt-4">
      <Button
        label="Cancel"
        @click="emit('noteSubmitted', props.order.id)"
        class="w-4/12 p-button-outlined"
      ></Button>
      <Button
        :loading="state.isLoading"
        @click="addNote"
        :label="state.showEditNote ? 'Save' : 'Add'"
        :disabled="!state.note.content.trim().length"
        class="w-4/12 ml-2 p-button-outlined p-button-secondary"
      ></Button>
    </div>
  </div>

  <div v-if="props.inventory">
    <div
      v-if="props.showTitle"
      class="mb-8 text-xl font-medium border-b text-900 dark:text-0"
    >
      Notes for inventory {{ props.inventory.id }}
    </div>
    <ul class="p-0 m-0 list-none">
      <li
        class="pb-4 mb-2 border border-b"
        v-for="note in props.inventory.note"
      >
        <!-- <div class="mb-2 font-medium text-900 dark:text-0">{{ note.title }}</div> -->
        <div
          class="mb-2 leading-normal text-900 dark:text-0"
          style="max-width: 30rem"
        >
          Created at {{ dfl(note.created_at) }} by {{ note.author?.full_name }}
        </div>
        <div
          class="leading-normal text-800 dark:text-50"
          style="max-width: 30rem"
        >
          {{ note.content }}
        </div>
      </li>
    </ul>
    <div
      v-if="state.showEditNote || computedOrder.note.length === 0"
      class="grid grid-cols-12 gap-4 mt-4 formgrid p-fluid"
    >
      <div class="col-span-12 mb-4 md:col-span-12">
        <p class="text-2xl">New Note</p>
      </div>
      <div class="col-span-12 mb-4 field md:col-span-6">
        <label
          for="street_address"
          class="text-sm text-base text-700 dark:text-100"
          >Content</label
        >
        <Textarea
          v-model="state.note.content"
          :autoResize="true"
          class="p-component p-inputtext-fluid"
          rows="5"
          cols="30"
        />
      </div>
    </div>
    <div class="flex justify-between pt-4">
      <Button
        label="Cancel"
        @click="emit('noteSubmitted', props.inventory.id)"
        class="w-4/12 p-button-outlined"
      ></Button>
      <Button
        :loading="state.isLoading"
        @click="addNoteInventory"
        :label="state.showEditNote ? 'Save' : 'Add'"
        :disabled="!state.note.content.trim().length"
        class="w-4/12 ml-2 p-button-outlined p-button-secondary"
      ></Button>
    </div>
  </div>
</template>

<script setup>
  import { computed, reactive, onMounted, inject } from "vue"
  import { useToast } from "primevue/usetoast"
  import cloneDeep from "lodash.clonedeep"
  import CustomerApi from "@/api/customers"
  import { dfl, dfc } from "@/service/DateFormat"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"

  const customerStore = useCustomerOrder()
  const customerApi = new CustomerApi()
  const usersStore = useUsers()

  const toast = useToast()
  const $isObjectPopulated = inject("$isObjectPopulated")
  const emit = defineEmits(["noteSubmitted"])

  const props = defineProps({
    order: {
      type: Object
    },
    inventory: {
      type: Object
    },
    close: {
      type: Function,
      default: () => {}
    },
    showTitle: {
      type: Boolean,
      default: true
    }
  })

  const addNoteInventory = () => {
    if (state.showEditNote) {
      saveNote()
    } else {
      state.showEditNote = true
    }
  }

  const addNote = () => {
    if (state.showEditNote) {
      saveOrder()
    } else {
      state.showEditNote = true
    }
  }

  const state = reactive({
    showEditNote: true,
    isLoading: false,
    note: {
      title: "",
      content: ""
    },
    notes_public: {}
  })

  const computedOrder = computed(() => {
    if (props.inventory != null) return
    const order = cloneDeep(customerStore.order)
    if (order) {
      order.note.sort((a, b) => {
        return new Date(a.created_at) - new Date(b.created_at)
      })
      return order
    }
    return null
  })

  const resetOrder = () => {
    state.note = {
      title: "",
      content: ""
    }
  }

  onMounted(() => {
    resetOrder()

    const notes = customerStore?.order?.note?.sort((a, b) => {
      return new Date(a.created_at) - new Date(b.created_at)
    })
    notes?.forEach((element) => {
      state.notes_public[element.id] = element.is_public == true ? true : false
    })
  })

  const saveNote = async () => {
    if (!$isObjectPopulated(state.note)) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Please enter a note",
        group: "br",
        life: 2000
      })
      return
    }
    state.isLoading = true

    const requestData = {
      title: state.note.content,
      content: state.note.content,
      inventory_id: props.inventory.id
    }

    const { data, error } = await customerApi.saveNote(requestData)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: error.value,
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Note added!",
        group: "br",
        life: 2000
      })
    }
    emit("noteSubmitted", props.inventory.id)
    state.isLoading = false
  }

  const saveOrder = async () => {
    if (!$isObjectPopulated(state.note)) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Please enter a note",
        group: "br",
        life: 2000
      })
      return
    }
    state.isLoading = true

    const requestData = {
      note: {
        title: state.note.content,
        content: state.note.content
      }
    }
    const { data, error } = await customerApi.updateOrder(
      computedOrder.value.id,
      requestData
    )

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: error.value,
        group: "br",
        life: 2000
      })
      state.isLoading = false
      return
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Note added!",
        group: "br",
        life: 2000
      })
      customerStore.setOrder(data.value)
      emit("noteSubmitted", data.value.id)
    }
    state.isLoading = false
    resetOrder()
  }

  const handleCheckChanged = async (note_id) => {
    const requestData = {
      id: note_id,
      content: state.notes_public[note_id] ? "public" : "private"
    }
    const { data, error } = await customerApi.updateNoteIsPublic(
      customerStore.order.id,
      requestData
    )

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: error.value,
        group: "br",
        life: 2000
      })

      if (state.notes_public[note_id]) {
        state.notes_public[note_id] = false
      }
    } else {
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Note visiblity changed!",
        group: "br",
        life: 2000
      })

      if (state.notes_public[note_id]) {
        for (let key in state.notes_public) {
          if (key != note_id) {
            state.notes_public[key] = false
          }
        }
      }
    }
  }
</script>
