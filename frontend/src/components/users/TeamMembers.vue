<template>
  <div class="mx-6 mt-4">
    <Toolbar class="mb-6">
      <template #start>
        <Button
          label="Refresh"
          icon="pi pi-circle-on"
          class="ml-4 p-button-success"
          :loading="state.loading"
          @click="refresh"
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
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      :rowsPerPageOptions="[10, 25, 50]"
      currentPageReportTemplate="Showing {first} to {last} of {totalRecords} users"
      responsiveLayout="scroll"
      :loading="state.loading"
      sortField="manager"
      :sortOrder="-1"
      :paginator="true"
      scrollHeight="80vh"
      scrollDirection="both"
      :rows="25"
      :value="filteredUsers"
      :filters="state.filters"
      class="w-full p-datatable-sm"
      style="min-width: 80%"
    >
      <template #header>
        <div class="flex flex-col table-header md:flex-row md:justify-start">
          <h5 class="mb-2 text-2xl md:m-0">Team & Assistants</h5>

          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText
              style="min-width: 20em"
              v-model="state.filters['global'].value"
              placeholder="Search any user"
            />
          </IconField>
        </div>
      </template>
      <Column field="first_name" header="Name" style="width: 120px">
        <template #body="slotProps">
          <Button
            class="p-button-rounded"
            :disabled="!$ability.can('update', 'user-change_team')"
            @click="openUser(slotProps.data)"
            :label="`${slotProps.data.full_name}`"
          />
        </template>
      </Column>
      <Column :sortable="true" field="team_lead" header="Manager">
        <template #body="slotProps">
          <Chip
            v-for="u in slotProps.data.team_lead"
            :label="u.team_member.full_name"
            class="mr-2"
          ></Chip>
        </template>
      </Column>
      <Column :sortable="true" field="manager" header="Agents">
        <template #body="slotProps">
          <Chip
            v-for="u in slotProps.data.manager"
            :label="u.assistant.full_name"
            class="mr-2"
          ></Chip>
        </template>
      </Column>
      <Column :sortable="true" field="assistant" header="Managed By">
        <template #body="slotProps">
          {{
            slotProps.data.assistant &&
            slotProps.data.assistant?.manager.full_name
          }}
        </template>
      </Column>
      <Column :sortable="true" field="team_member" header="Team member of">
        <template #body="slotProps">
          {{
            slotProps.data.team_member &&
            slotProps.data.team_member?.team_lead?.full_name
          }}
        </template>
      </Column>
    </DataTable>

    <Dialog
      v-model:visible="state.userDialog"
      maximizable
      dismissableMask
      closeOnEscape
      :style="{ maxWidth: '1100px' }"
      header="Update User"
      :modal="true"
      class="p-fluid"
    >
      <ManageUserTeam @hide="state.userDialog = false" :userProp="state.user" />
    </Dialog>
  </div>
</template>

<script setup>
  import UserTeam from "@/components/users/UserTeam.vue"
  import { reactive, computed, onMounted, inject } from "vue"
  import { useUsers } from "@/store/modules/users"
  import { useAuth0 } from "@auth0/auth0-vue"
  import { useToast } from "primevue/usetoast"
  import UsersService from "../../service/User"
  import UserApi from "../../api/user"
  import cloneDeep from "lodash.clonedeep"
  import ManageUserTeam from "./ManageUserTeam.vue"
  import { FilterMatchMode } from "@primevue/core/api"
  const $ability = inject("$ability")

  const toast = useToast()
  const userStore = useUsers()
  const usersService = new UsersService()
  const userApi = new UserApi()

  const filteredUsers = computed(() => {
    return userStore.users.filter((u) => u)
  })

  const state = reactive({
    loading: false,
    filters: {},
    userDialog: false
  })

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  const openUser = async (user) => {
    if (user.id) {
      state.user = userStore.users.find((u) => u.id === user.id)
    } else {
      state.user = {}
    }
    state.userDialog = true
  }

  const refresh = async () => {
    state.loading = true
    userStore.$reset()
    if (userStore.users.length === 0) {
      const { data } = await userApi.getUsers()
      const users = data.value.map((l) => usersService.dtoUser(l))
      userStore.setUsers(users)
    }

    state.loading = false
  }

  const exportCSV = async (type) => {
    let data = []
    filteredUsers.value.forEach((el) => {
      let obj = {}
      obj["name"] = el.full_name
      obj["agents"] = ""
      el.manager.forEach((u) => {
        obj["agents"] += u.assistant.full_name + " | "
      })
      obj["manager"] = ""
      el.team_lead.forEach((u) => {
        obj["manager"] += u.team_member.full_name + " | "
      })
      data.push(obj)
    })
    data.sort((a, b) => b.agents.length - a.agents.length)
    const headers = Object.keys(data[0])

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [
        headers.join(","),
        ...data.map((obj) =>
          headers
            .map((key) => {
              if (obj[key] == undefined) {
                return ""
              } else {
                return obj[key].toString().replace(/,/g, "")
              }
            })
            .join(",")
        ),
        ,
      ].join("\n")

    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", "Teams")
    document.body.appendChild(link)
    link.click()
    /*
      let data_summary = fetchExportData("all_sales");
      if (!data_summary) {
        return;
      }

      const headers_summary = Object.keys(data_summary[0]);
      let data_taxable = fetchExportData("taxable_sales");

      if (!data_taxable) {
        return;
      }
      const headers_taxable = ['order_id', 'created', 'name', 'total_paid', 'total_tax_paid', 'calculated_shipping_revenue_total', 'calculated_line_item_title']
      let data_non_taxable = fetchExportData("non_taxable_sales");

      if (!data_non_taxable) {
        return;
      }

      const headers_non_taxable = ['order_id', 'created', 'name', 'total_paid', 'calculated_shipping_revenue_total', 'calculated_line_item_title']


      const csvContent =
        "data:text/csv;charset=utf-8," +
        [
          headers_summary.join(","),
          ...data_summary.map((obj) =>
            headers_summary
              .map((key) => {
                if (obj[key] == undefined) {
                  return "";
                } else {
                  return obj[key].toString().replace(/,/g, "");
                }
              })
              .join(",")
          ),
          "",
          headers_taxable.join(","),
          ...data_taxable.map((obj) =>
            headers_taxable
              .map((key) => {
                if (obj[key] == undefined) {
                  return "";
                } else {
                  return obj[key].toString().replace(/,/g, "");
                }
              })
              .join(",")
          ),
          "",
          headers_non_taxable.join(","),
          ...data_non_taxable.map((obj) =>
            headers_non_taxable
              .map((key) => {
                if (obj[key] == undefined) {
                  return "";
                } else {
                  return obj[key].toString().replace(/,/g, "");
                }
              })
              .join(",")
          ),
        ].join("\n");

      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", type.title);
      document.body.appendChild(link);
      link.click();
      return;*/
  }

  initFilters()

  onMounted(async () => {})
</script>
