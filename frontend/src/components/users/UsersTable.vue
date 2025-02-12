<template>
  <div v-if="$ability.can('read', 'navigation-users')">
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            label="Add User"
            icon="pi pi-plus"
            class="ml-4 p-button-success"
            @click="openUser"
            :disabled="!$ability.can('update', 'user-create_user')"
          />
        </template>

        <template #end>
          <Button
            label="Export"
            icon="pi pi-upload"
            class="p-button-help"
            @click="exportCSV($event)"
          />
        </template>
      </Toolbar>
      <DataTable
        v-if="!state.loading"
        ref="dt"
        :value="userStore.users"
        :style="`width: ${tableWidth}`"
        scrollHeight="60vh"
        dataKey="id"
        :paginator="true"
        scrollDirection="both"
        :rows="25"
        :filters="state.filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} Users"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex flex-col items-start">
            <h5 class="mb-2">Users</h5>
            <div class="flex items-center space-x-2">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="state.filters['global'].value"
                placeholder="Search..."
              />
            </div>
          </div>
        </template>
        <Column field="id" header="User Id" style="width: 120px">
          <template #body="slotProps">
            <Button
              class="p-button-rounded"
              @click="openUser(slotProps.data)"
              :disabled="!$ability.can('update', 'user-update_user')"
              >{{ slotProps.data.id.substring(0, 4) }}</Button
            >
          </template>
        </Column>
        <Column
          v-for="(col, i) in userService.columnOrdering"
          :key="col.order_id + col.line_item_id + i.toString()"
          :field="col.field"
          :header="col.display"
          :sortable="col.sortable"
          :style="col.style"
        >
          <template v-if="col?.isButton" #body="slotProps">
            <Button
              class="p-button-rounded p-button-text p-button-sm"
              @click="manageButton(col, slotProps.data)"
              :loading="state.loadingResetPassword"
              >{{
                col.field === "sales_link"
                  ? slotProps.data.sales_link
                  : col.display
              }}</Button
            >
          </template>
        </Column>
      </DataTable>
      <LoadingTable
        v-if="state.loading"
        :columns="userService.columnOrdering"
        :loading="state.loading"
      />
    </div>
    <Dialog
      v-model:visible="state.userDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      :header="state.user?.id ? 'Update User' : 'Create User'"
      :modal="true"
      class="p-fluid"
    >
      <create-user @hide="state.userDialog = false" :userProp="state.user" />
    </Dialog>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, ref } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import UserService from "@/service/User"
  import UserApi from "@/api/user"
  import CreateUser from "./CreateUser.vue"
  import { useUsers } from "@/store/modules/users"
  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"

  const $ability = inject("$ability")

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const toast = useToast()
  const userStore = useUsers()

  const userService = new UserService()
  const userApi = new UserApi()

  const { user } = useAuth0()
  const authUser = user

  const smAndSmaller = breakpoints.isSmallerOrEqual("sm") // sm and larger
  const largerThanSm = breakpoints.greater("sm") // only larger than sm
  const lgAndSmaller = breakpoints.smallerOrEqual("lg") // lg and smaller
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg") // only smaller than lg

  const state = reactive({
    user: {},
    users: [],
    userDialog: false,
    loading: false,
    noteDialog: false,
    filters: {}
  })

  const dt = ref()

  const tableWidth = computed(() => {
    if (greaterOrEqualLarge.value) {
      return "92vw"
    } else if (lgAndSmaller.value) {
      return "92vw"
    } else if (largerThanSm.value) {
      return "90vw"
    }
  })

  const currentUser = computed(() => {
    return userStore.users.find((u) => u.email === authUser.value.email)
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  onMounted(async () => {
    state.loading = true
    if (userStore.users.length === 0) {
      const { data } = await userApi.getUsers()
      const users = data.value.map((l) => userService.dtoUser(l))
      userStore.setUsers(users)
    }
    state.loading = false
  })

  const exportCSV = () => dt.value.exportCSV()

  const openUser = async (user) => {
    if (user.id) {
      state.user = await getUserById(user.id)
    } else {
      state.user = {}
    }
    state.userDialog = true
  }

  const manageButton = async (col, slotData) => {
    if (col.field === "sales_link") {
      navigator.clipboard.writeText(slotData.sales_link).then(
        () => {},
        () => {}
      )
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Copied to clipboard",
        group: "br",
        life: 5000
      })
    }

    if (col.field === "send_password_email") {
      const { data, error } = await userApi.sendPasswordResetEmail(slotData.id)
      console.log(data.value.message)
      navigator.clipboard.writeText(data.value.message).then(
        () => {},
        () => {}
      )
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Copied to clipboard",
        group: "br",
        life: 5000
      })
    }
  }

  const getUserById = async (id) => {
    state.singleOrderLoading = true
    const { data, error } = await userApi.getUserById(id)

    if (error.value) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading user",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.loading = false
      return userService.dtoUser(data.value)
    }
  }
</script>

<style lang="scss" scoped>
  .table-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    @media screen and (max-width: 960px) {
      align-items: start;
    }
  }
</style>
