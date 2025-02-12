<template>
  <div>
    <div class="mx-6 mt-4">
      <Toolbar class="mb-6">
        <template #start> </template>

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
        responsiveLayout="scroll"
        :loading="state.loading"
        scrollHeight="80vh"
        scrollDirection="both"
        :rows="25"
        :value="state.roles"
        :filters="state.filters"
        class="w-full p-datatable-lg"
        style="min-width: 80%"
      >
        <template #header>
          <div>
            <h5 class="mb-2 text-2xl md:m-0">Roles</h5>
            <span class="ml-4 p-input-icon-left">
              <IconField>
                <InputIcon class="pi pi-search" />
                <InputText
                  style="min-width: 20em"
                  v-model="state.filters['global'].value"
                  placeholder="Search any role"
                />
              </IconField>
            </span>
            <Button
              label="Save"
              class="ml-4 p-button-raised p-button-rounded p-button-success"
              @click="updateRolePermissions()"
              :loading="state.loading"
            ></Button>

            <!-- <Button
              label="Add Role"
              class="ml-4 p-button-raised p-button-rounded p-button-success"
              @click="showRoleDialog()"
            ></Button> -->
          </div>
        </template>
        <Column field="name" header="Role"></Column>
        <Column field="permissions" header="Permissions">
          <template #body="slotProps">
            <Button
              v-if="slotProps.data.permissions == undefined"
              v-model="state.newRoleName"
              :loading="state.roles_loading[slotProps.data.id]"
              label="Click to load"
              @click="loadPermissionsForRole(slotProps.data.id)"
              :disabled="
                slotProps.data.name === 'admin' ||
                slotProps.data.name === 'superadmin'
              "
            />
            <MultiSelect
              v-if="slotProps.data.permissions"
              :filter="true"
              filter
              v-model="slotProps.data.permissions"
              :options="mappedPermissions"
              display="chip"
              optionLabel="label"
              optionValue="value"
              placeholder="Select Permissions"
              style="max-width: 600px"
              :disabled="
                slotProps.data.name === 'admin' ||
                slotProps.data.name === 'superadmin'
              "
            />
          </template>
        </Column>
        <Column header="Duplicate Role">
          <template #body="slotProps">
            <Button
              label="Duplicate"
              class="p-button-raised p-button-rounded p-button-success"
              :disabled="slotProps.data.permissions == undefined"
              @click="openRoleDuplicationDialog(slotProps.data)"
            />
          </template>
        </Column>
        <Column header="Default Commission">
          <template #body="slotProps">
            {{ slotProps.data.sales_commission_rate }}%
          </template>
        </Column>
        <Column header="Rental Commission">
          <template #body="slotProps">
            {{ $fc(slotProps.data.rental_commission_rate) }}
          </template>
        </Column>

        <Column header="Update Rates">
          <template #body="slotProps">
            <Button
              label="Update"
              class="p-button-raised p-button-rounded p-button-success"
              @click="editRoleCommissions(slotProps.data)"
            />
          </template>
        </Column>
        <Dialog
          v-model:visible="state.duplicateRoleDialog"
          dismissableMask
          closeOnEscape
          :style="{ maxWidth: '1100px' }"
          :header="`Duplicating Role ${state.originalRole.name}`"
          :modal="true"
          class="p-fluid"
        >
          <InputText
            class="my-2"
            v-model="state.newRoleName"
            placeholder="New Role Name"
            id="NewRoleName"
          />

          <Button
            label="Save new role"
            class="p-button-raised p-button-rounded p-button-success"
            :loading="state.loading"
            @click="saveNewRole()"
          />
        </Dialog>
        <Dialog
          v-model:visible="state.editRates"
          dismissableMask
          closeOnEscape
          :style="{ maxWidth: '400px' }"
          :header="`Edit Rates For ${state.role_name}`"
          :modal="true"
          class="p-fluid"
        >
          <label>Default Commission Rate</label>
          <InputText
            class="p-component p-inputtext-fluid"
            v-model="state.sales_commission_rate"
            placeholder="Default Commission Rate"
            id="NewRoleName"
          />
          <label>Rental Commission Rate</label>
          <InputText
            class="p-component p-inputtext-fluid"
            v-model="state.rental_commission_rate"
            placeholder="Rental Commission Rate"
            id="NewRoleName"
          />
          <hr />
          <Tag class="p-2 mb-2 bg-red-300 text-l"
            >Default role rates do not override exceptions to role rates. Please
            check your users individual rates and override as necessary</Tag
          >
          <Button
            label="Update"
            class="p-button-raised p-button-rounded p-button-success"
            :loading="state.loading"
            @click="editRoleRate()"
          />
        </Dialog>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, ref, inject } from "vue"
  import { useToast } from "primevue/usetoast"
  import RoleApi from "../../api/roles"
  import cloneDeep from "lodash.clonedeep"
  import { FilterMatchMode } from "@primevue/core/api"
  const $fc = inject("$formatCurrency")

  const toast = useToast()
  // const roleStore = useRoles();
  const roleApi = new RoleApi()

  const state = reactive({
    loading: false,
    filters: {},
    roleDialog: false,
    duplicateRoleDialog: false,
    originalRole: "",
    newRoleName: "",
    roles: [],
    originalRoles: [],
    role: {},
    permissions: [],
    roles_loading: {},
    role_name: "",
    sales_commission_rate: 0.0,
    rental_commission_rate: 0.0,
    role_id: "",
    editRates: false
  })

  const mappedPermissions = computed(() => {
    return state.permissions.map((p) => {
      return { label: p.value, value: p.value }
    })
  })
  const dt = ref()
  const exportCSV = () => dt.value.exportCSV()

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  const openRoleDuplicationDialog = (roleName) => {
    state.originalRole = roleName
    state.duplicateRoleDialog = true
  }

  const editRoleCommissions = (role) => {
    state.role_name = role.name
    state.role_id = role.id
    state.sales_commission_rate = role.sales_commission_rate || 0
    state.rental_commission_rate = role.rental_commission_rate || 0
    state.editRates = true
  }
  const editRoleRate = async () => {
    state.loading = true
    const res = await roleApi.editRateRole({
      role_id: state.role_id,
      name: state.role_name,
      sales_commission_rate: state.sales_commission_rate,
      rental_commission_rate: state.rental_commission_rate
    })
    await getAllRolesAndPermissions()
    state.loading = false
    state.editRates = false
  }

  const loadPermissionsForRole = async (role_id) => {
    state.roles_loading[role_id] = true

    const { data, error } = await roleApi.getPermissionsForRole(role_id)

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Permissions couldn't be loaded.",
        life: 3000
      })
      return
    }

    state.roles.forEach((role) => {
      if (role.id == role_id) {
        role.permissions = data.value.map((el) => {
          return el.permission_name
        })
      }
    })

    state.originalRoles.forEach((role) => {
      if (role.id == role_id) {
        role.permissions = data.value.map((el) => {
          return el.permission_name
        })
      }
    })

    state.roles_loading[role_id] = false
  }

  const saveNewRole = () => {
    state.loading = true
    if (state.newRoleName === "") {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Please enter a new role name",
        life: 3000
      })
      return
    }

    let newRole = {
      role_name: state.newRoleName,
      role_id: state.originalRole.id
    }

    roleApi
      .duplicateRole(newRole)
      .then(async () => {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Role created",
          life: 3000
        })
        await getAllRolesAndPermissions()
        state.duplicateRoleDialog = false
      })
      .catch((e) => {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error creating role",
          life: 3000
        })
      })
  }

  const getAddedRemoved = (original, current) => {
    let added = current.filter((c) => {
      return !original.find((o) => o.value === c.value)
    })
    let removed = original.filter((o) => {
      return !current.find((c) => c.value === o.value)
    })
    return { added, removed }
  }

  const updateRolePermissions = async () => {
    state.loading = true
    Promise.all(
      state.roles.map(async (r) => {
        if (r.permissions == undefined) {
          return
        }
        const changed = getAddedRemoved(
          state.originalRoles
            .find((role) => role.id === r.id)
            .permissions.map((p) => {
              return { value: p }
            }),
          r.permissions.map((p) => {
            return { value: p }
          })
        )

        const mappedAdded = changed.added.map((p) => {
          return state.permissions.find((per) => per.value === p.value)
        })

        const mappedRemoved = changed.removed.map((p) => {
          return state.permissions.find((per) => per.value === p.value)
        })

        if (mappedAdded.length === 0 && mappedRemoved.length === 0) {
          throw new Error("No changes to save")
        }

        if (mappedAdded.length > 0) {
          await roleApi.addPermissionToRole(r.id, mappedAdded)
        }

        if (mappedRemoved.length > 0) {
          await roleApi.removePermissionFromRole(r.id, mappedRemoved)
        }
      })
    )
      .then((r) => {
        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Role permissions updated",
          life: 3000,
          group: "br"
        })
      })
      .catch((e) => {
        // toast.add({
        //   severity: "error",
        //   summary: "Error",
        //   detail: e,
        //   life: 3000,
        //   group: "br",
        // });
      })
    state.loading = false
  }

  const getAllRolesAndPermissions = async () => {
    state.loading = true
    let rates = await roleApi.getRoleRates()
    rates = rates.data.value
    let r = await roleApi.getRoles()
    const res = await roleApi.getPermissions()
    state.permissions = res.data.value
    state.originalRoles = cloneDeep(r.data.value)
    state.roles = r.data.value.map((current_role) => {
      let filtered_rate = rates.filter((e) => e.role_id == current_role.id)
      if (filtered_rate.length > 0) {
        return {
          ...current_role,
          sales_commission_rate: filtered_rate[0].sales_commission_rate,
          rental_commission_rate: filtered_rate[0].rental_commission_rate
        }
      }
      return {
        ...current_role,
        sales_commission_rate: 0,
        rental_commission_rate: 0
      }
    })
    state.loading = false
  }

  onMounted(async () => {
    await getAllRolesAndPermissions()
  })
</script>
