<template>
  <ConfirmPopup></ConfirmPopup>
  <div>
    <div class="mt-1">
      <div>
        <div class="ml-5 text-2xl font-medium text-900 dark:text-0">Orders</div>
      </div>
    </div>
    <div class="mt-2 tool-bar">
      <div v-if="smAndSmaller" class="grid grid-cols-12 gap-4">
        <div class="flex flex-col items-center w-full col-span-12">
          <!-- <InputGroup> -->
          <InputText
            :disabled="state.loading"
            style="min-width: 10em"
            v-model="state.quickSearch"
            :placeholder="`Search order id`"
            @keypress="quickSearch"
            class="p-4"
          />
          <Button
            class="p-4 ml-1"
            icon="pi pi-search"
            slot="right-icon"
            :loading="state.quickSearchLoading"
            @click="quickSearch(null)"
          />
          <!-- </InputGroup> -->
        </div>
        <div class="col-span-2">
          <Button
            v-if="state.quickSearchOrder.length > 0"
            class="p-4 ml-1 p-button-secondary"
            icon="pi pi-refresh"
            slot="right-icon"
            @click="quickSearchReset"
          />
        </div>
        <div class="col-span-12 overflow-x-scroll" style="max-width: 95vw">
          <SelectButton
            class="p-2 ml-2"
            v-if="!state.searchAndFilter && categories.length > 0"
            v-model="state.selectedCategory"
            :options="categories"
            optionLabel="name"
            placeholder="Select a category"
            :pt="{
              root: {
                class: 'categories-button'
              }
            }"
          />
        </div>
        <div class="flex flex-col items-center w-full col-span-12">
          <Button
            v-if="!state.searchAndFilter && smAndSmaller"
            label="Global Refresh"
            icon="pi pi-refresh"
            class="p-4 p-button-secondary"
            :loading="state.globalRefreshLoading"
            @click="globalRefresh"
            size="large"
          />
          <Button
            v-if="!state.searchAndFilter && smAndSmaller"
            :label="
              state.resultCount === state.customerRawLength
                ? `All ${customersStore.currentOrderStatus} pulled`
                : `Pull All ${currentStatusComp}`
            "
            :disabled="state.resultCount === state.customerRawLength"
            icon="pi pi-download"
            class="p-4 mt-4 p-button-secondary"
            :loading="state.loading"
            @click="getAllInvoices"
            size="large"
          />
          <ToggleButton
            v-model="state.searchAndFilter"
            onLabel="All Invoices "
            offLabel="Search & Filter"
            onIcon="pi pi-file"
            offIcon="pi pi-search-plus"
            class="mt-4 p-button-primary"
          />
        </div>
        <div v-if="smAndSmaller" class="grid grid-cols-2 col-span-12 gap-4 p-5">
          <Tag class="col-span-1 p-2 text-xl bg-blue-300" value="PU A"></Tag>
          <Tag class="col-span-1 p-2 text-xl pu_b" value="PU B"></Tag>
          <Tag class="col-span-1 p-2 text-xl bg-orange-300" value="PU C"></Tag>
        </div>
        <div
          v-if="smAndSmaller"
          class="grid grid-cols-4 col-span-12 gap-4 pl-5 pr-5"
        >
          <Tag
            class="col-span-1 p-2 text-xl"
            v-for="(item, index) in state.logistics_zones"
            :key="index"
            :value="item.zone_name"
            :style="{ backgroundColor: item.color }"
          ></Tag>
        </div>
      </div>
      <Toolbar class="mb-6" v-if="!smAndSmaller">
        <template #start>
          <InputText
            :disabled="state.loading"
            style="min-width: 10em"
            v-model="state.quickSearch"
            :placeholder="`Search order id`"
            @keypress="quickSearch"
          />
          <Button
            class="ml-1"
            icon="pi pi-search"
            slot="right-icon"
            :loading="state.quickSearchLoading"
            @click="quickSearch(null)"
          />
          <Button
            v-if="state.quickSearchOrder.length > 0"
            class="ml-1 p-button-secondary"
            icon="pi pi-refresh"
            slot="right-icon"
            @click="quickSearchReset"
          />

          <SelectButton
            class="ml-2"
            v-if="!state.searchAndFilter && categories.length > 0"
            v-model="state.selectedCategory"
            :options="categories"
            optionLabel="name"
            :pt="{
              root: {
                class: 'categories-button'
              }
            }"
            placeholder="Select a category"
          />
        </template>
        <template #center>
          <Button
            v-if="!state.searchAndFilter && !smAndSmaller"
            label="Global Refresh"
            icon="pi pi-refresh"
            class="ml-4 p-button-secondary"
            :loading="state.globalRefreshLoading"
            @click="globalRefresh"
          />
          <Button
            v-if="!state.searchAndFilter && !smAndSmaller"
            :label="
              state.resultCount === state.customerRawLength
                ? `All ${customersStore.currentOrderStatus} pulled`
                : `Pull All ${currentStatusComp}`
            "
            :disabled="state.resultCount === state.customerRawLength"
            icon="pi pi-download"
            class="ml-4 p-button-secondary"
            :loading="state.loading"
            @click="getAllInvoices"
          />
          <ToggleButton
            v-model="state.searchAndFilter"
            onLabel="All Invoices "
            offLabel="Search & Filter"
            onIcon="pi pi-file"
            offIcon="pi pi-search-plus"
            class="ml-4 p-button-primary"
          />
          <template v-if="usersStore.cms?.feature_flags?.order_row_coloring">
            <div v-if="!smAndSmaller" class="ml-2">
              <Tag class="p-2 text-xl bg-blue-300" value="PU A"></Tag>
            </div>
            <div v-if="!smAndSmaller" class="ml-2">
              <Tag class="p-2 text-xl pu_b" value="PU B"></Tag>
            </div>
            <div v-if="!smAndSmaller" class="ml-2">
              <Tag class="p-2 text-xl bg-orange-300" value="PU C"></Tag>
            </div>
            <div
              v-if="!smAndSmaller"
              class="ml-2"
              v-for="(item, index) in state.logistics_zones"
              :key="index"
            >
              <Tag
                class="p-2 text-xl"
                :style="{ backgroundColor: item.color }"
                :value="item.zone_name"
              ></Tag>
            </div>
          </template>
        </template>
        <template #end>
          <div class="export-switch-container">
            <label
              class="block font-medium text-blue-600 text-900 dark:text-0 label-input-switch"
              >{{ state.exportOrders ? "Export Orders" : "Export Line Items" }}
            </label>
            <ToggleSwitch
              class="export-orders-switch"
              v-model="state.exportOrders"
              @mouseover="showTooltip = true"
              @mouseleave="showTooltip = false"
            />
            <div v-if="showTooltip" class="tooltip">
              Export as Orders csv if on or export as Line Items csv if off.
            </div>
          </div>
          <Button
            v-if="!smAndSmaller"
            label="Export"
            :disabled="!$ability.can('download', 'orders')"
            icon="pi pi-upload"
            class="p-button-help"
            @click="exportCSV($event)"
          />
        </template>
      </Toolbar>
      <div>
        <StatusHeader v-if="!state.searchAndFilter" />
        <DataTable
          v-if="
            !state.loading &&
            !state.offlineModeLoading &&
            usersStore.currentUser
          "
          :value="filteredCustomerOrders || []"
          :paginator="true"
          :rows="50"
          :style="`width: ${tableWidth}`"
          :filters="state.filters"
          :scrollable="true"
          class="p-datatable-sm"
          scrollHeight="60vh"
          dataKey="line_item_id"
          ref="dt"
          :rowClass="rowClass"
          scrollDirection="both"
          editMode="cell"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          :rowsPerPageOptions="[10, 25, 50, 100]"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} orders"
          responsiveLayout="scroll"
          @cell-edit-complete="onCellEditComplete"
          @rowExpand="onRowExpand"
          @page="onPage"
          :sortField="sortField"
          :sortOrder="-1"
        >
          <template #header>
            <SearchFilterTable v-if="state.searchAndFilter" />
            <div
              class="flex flex-col table-header md:flex-row md:justify-start"
            >
              <!-- <h5 class="mb-2 md:m-0 p-as-md-center"></h5> -->
              <span class="mb-4 ml-4 p-input-icon-left">
                <IconField>
                  <i class="pi pi-search" />
                  <InputText
                    style="min-width: 20em"
                    v-model="state.filters['global'].value"
                    :placeholder="`Search anything under`"
                  />
                </IconField>
              </span>
            </div>
          </template>

          <template #empty> No orders found. </template>
          <Column
            :frozen="true"
            field="order_display_order_id"
            header="Order"
            style="width: 100px"
            :sortable="true"
          >
            <template #body="slotProps">
              <Button
                :loading="
                  state.individualOrderLoading === slotProps.data.line_item_id
                "
                :class="buttonClass(null, null)"
                @click="openButton('order_display_order_id', slotProps.data)"
                >{{ slotProps.data.order_display_order_id }}
              </Button>
            </template>
          </Column>
          <Column
            v-for="(col, i) in filteredColumns"
            :key="col.order_id + col.line_item_id + i.toString()"
            :field="col.field"
            :header="col.display"
            :sortable="col.sortable"
            :style="col.style"
          >
            <template v-if="col.isButton" #body="slotProps">
              <Button
                :class="buttonClass(slotProps, col.field)"
                @click="openButton(col.field, slotProps.data)"
                :label="
                  slotProps.data.order_note?.length > 0 ? 'Notes' : 'Add Note'
                "
              />
            </template>

            <template v-if="col?.dropdown" #body="slotProps">
              <Tag
                class="bg-blue-300"
                v-if="
                  col.field === 'line_item_potential_driver_id' &&
                  slotProps.data[col.field] &&
                  !$ability.can('read', 'order_column-potential_driver_id')
                "
              >
                <i class="pi pi-check"></i>
              </Tag>
              <Tag
                class="bg-blue-300"
                v-else-if="
                  col.field === 'line_item_potential_driver_id' &&
                  !slotProps.data[col.field] &&
                  !$ability.can('read', 'order_column-potential_driver_id')
                "
              >
                <i class="pi pi-times"></i>
              </Tag>
              <Select
                v-else-if="
                  col.field !== 'line_item_welcome_call' &&
                  col.field !== 'line_item_good_to_go'
                "
                :loading="state.loadingLineItem === slotProps.data.line_item_id"
                @change="onCellEditComplete($event, col, slotProps.data)"
                :showClear="col.field === 'line_item_potential_driver_id'"
                @click="loadDriversList(col.field)"
                v-model="slotProps.data[col.field]"
                :options="
                  typeof col.dropdown === 'object' ? col.dropdown : driversList
                "
                optionLabel="label"
                optionValue="value"
                :class="rowClass(slotProps.data)"
                :placeholder="`Select ${col.display}`"
              />
              <Select
                v-else-if="
                  col.field === 'line_item_welcome_call' ||
                  col.field === 'line_item_good_to_go'
                "
                :loading="state.loadingLineItem === slotProps.data.line_item_id"
                @change="onCellEditComplete($event, col, slotProps.data)"
                :class="yesNoInProgressClass(slotProps.data[col.field])"
                v-model="slotProps.data[col.field]"
                :options="col.dropdown"
                optionLabel="label"
                optionValue="value"
              />
            </template>

            <template v-if="col?.isAmount" #body="{ data, field }">
              {{ $fc(data[field]) }}
            </template>
            <template
              v-if="col?.field == 'line_item_inventory_total_cost'"
              #body="{ data, field }"
            >
              {{ $fc(data["line_item_inventory"]?.total_cost || 0) }}
            </template>
            <template v-if="col?.isBool" #body="{ data, field }">
              {{ data[field] ? "Yes" : "No" }}
            </template>

            <template
              v-if="col.field === 'order_calculated_paid_in_full_date'"
              #body="slotProps"
            >
              {{ slotProps.data.order_calculated_paid_date_rental }}
            </template>
            <template v-if="col.field === 'order_signed_at'" #body="slotProps">
              {{ slotProps.data.order_signed_at }}
            </template>

            <template
              v-if="col.field === 'order_calculated_signed_date'"
              #body="slotProps"
            >
              {{ getSignedDate(slotProps.data) }}
            </template>

            <template v-if="col.field === 'customer_phone'" #body="slotProps">
              {{ getCustomerPhone(slotProps.data) }}
            </template>

            <template v-if="col.field === 'customer_email'" #body="slotProps">
              {{ getCustomerEmail(slotProps.data) }}
            </template>

            <template
              v-if="col.field === 'customer_full_name'"
              #body="slotProps"
            >
              {{ nameField(slotProps.data) }}
            </template>

            <template
              v-if="col.field === 'line_item_inventory_container_number'"
              #body="slotProps"
            >
              <Tag
                class="bg-blue-300"
                @click="
                  copyColumnToClipboard(
                    $event,
                    slotProps.data.line_item_id,
                    col.field
                  )
                "
                :value="
                  slotProps.data['line_item_inventory'] != null
                    ? slotProps.data['line_item_inventory']['container_number']
                    : 'None'
                "
                :severity="'secondary'"
              />
            </template>
            <template
              v-if="
                col.field === 'line_item_inventory_container_release_number'
              "
              #body="slotProps"
            >
              <Tag
                class="bg-blue-300"
                v-if="$ability.can('read', 'order_column-container_release')"
                @click="
                  copyColumnToClipboard(
                    $event,
                    slotProps.data.line_item_id,
                    col.field
                  )
                "
                :value="
                  slotProps.data[
                    'line_item_inventory_container_release_number'
                  ] || 'Not Attached'
                "
                :severity="'secondary'"
              />
              <Tag
                class="bg-blue-300"
                v-else-if="
                  slotProps.data[
                    'line_item_inventory_container_release_number'
                  ] && !$ability.can('read', 'order_column-container_release')
                "
              >
                <i class="pi pi-check"></i>
              </Tag>
              <Tag
                class="bg-blue-300"
                v-else-if="
                  !slotProps.data[
                    'line_item_inventory_container_release_number'
                  ] && !$ability.can('read', 'order_column-container_release')
                "
              >
                <i class="pi pi-times"></i>
              </Tag>
              <p v-else></p>
            </template>
            <template
              v-if="col.field == 'line_item_driver.company_name'"
              #body="slotProps"
            >
              <p
                v-if="
                  slotProps.data.line_item_driver?.company_name &&
                  $ability.can('read', 'order_column-potential_driver_id')
                "
              >
                {{ slotProps.data.line_item_driver?.company_name }}
              </p>
              <Tag
                class="bg-blue-300"
                v-else-if="
                  slotProps.data.line_item_driver?.company_name &&
                  !$ability.can('read', 'order_column-potential_driver_id')
                "
              >
                <i class="pi pi-check"></i>
              </Tag>
              <p v-else></p>
            </template>

            <template v-if="col?.isDatepicker" #body="slotProps">
              <DatePicker
                :disabled="!$ability.can('update', col?.updateAbility)"
                :loading="state.loadingLineItem === slotProps.data.line_item_id"
                inputId="basic"
                :style="col.style"
                :class="rowClass(slotProps.data)"
                showButtonBar
                @clear-click="onCellEditComplete($event, col, slotProps.data)"
                dateFormat="m/d/y"
                @date-select="onCellEditComplete($event, col, slotProps.data)"
                v-model="slotProps.data[col.field]"
              />
            </template>
            <template v-if="col?.isInput" #body="{ data, field }">
              <Button
                @click="
                  state.selectedAddButton = `${col.field}${data.line_item_id}`
                "
                :loading="
                  state.loadingLineItem === `${field}${data.line_item_id}`
                "
                :label="displayField(data, field)"
                class="p-button-text p-button-plain p-button-sm"
              />
            </template>

            <template v-if="col?.isInput" #editor="{ data, field }">
              <template
                v-if="
                  `${field}${data.line_item_id}` === state.selectedAddButton &&
                  field === 'line_item_note'
                "
              >
                <InputText
                  v-model="data[field]"
                  :placeholder="`Enter ${col.display}`"
                  autofocus
                  :class="rowClass(data)"
                />
              </template>

              <template
                v-if="
                  `${col.field}${data.line_item_id}` ===
                    state.selectedAddButton && col.field !== 'line_item_note'
                "
              >
                <InputText
                  v-model="data[field]"
                  :placeholder="`Enter ${col.display}`"
                  autofocus
                  :class="rowClass(data)"
                />
              </template>
            </template>
          </Column>
          <Column
            :frozen="true"
            field="line_item_calculated_accessory_commission"
            header="Manager Commission"
            style="width: 100px"
            :sortable="true"
          >
            <template #body="slotProps">
              <p v-if="slotProps.data['order_calculated_is_manager'] == true">
                {{
                  $fc(
                    slotProps.data["line_item_calculated_accessory_commission"]
                  )
                }}
              </p>
              <p v-else>{{ $fc(0) }}</p>
            </template>
          </Column>
          <Column
            :frozen="true"
            field="line_item_calculated_accessory_commission"
            header="Agent Commission"
            style="width: 100px"
            :sortable="true"
          >
            <template #body="slotProps">
              <p v-if="slotProps.data['order_calculated_is_manager'] == false">
                {{
                  $fc(
                    slotProps.data["line_item_calculated_accessory_commission"]
                  )
                }}
              </p>
              <p v-else>{{ $fc(0) }}</p>
            </template>
          </Column>
          <Column
            :frozen="true"
            field="line_item_vendor_name"
            header="Vendor"
            style="width: 100px"
            :sortable="true"
            v-if="$ability.can('read', 'vendors')"
          >
            {{ line_item_vendor_name }}
          </Column>
        </DataTable>
        <LoadingTable
          v-if="state.loading || state.offlineModeLoading"
          :columns="filteredColumns"
          :loading="state.loading"
        />
      </div>
      <Dialog
        v-model:visible="state.noteDialog"
        closeOnEscape
        :style="{ width: '50rem' }"
        modal
      >
        <NoteDetail
          :order="customersStore.order"
          @noteSubmitted="onNoteSubmitted"
        />
      </Dialog>
      <Dialog
        v-model:visible="state.updateOrderDialog"
        closeOnEscape
        :dismissableMask="true"
        :style="{ width: '100rem' }"
        modal
        :draggable="false"
        @hide="emptyOrder"
      >
        <template :class="smAndSmaller ? 'h-full' : ''" #header class="w-full">
          <div class="flex flex-wrap items-start gap-1">
            <div>
              <p :class="smAndSmaller ? 'text-lg' : 'text-3xl'">
                Invoice - {{ state.customerOrder.display_order_id }} ({{
                  state.customerOrder.type
                }})<span
                  class="ml-8 text-xl"
                  style="background-color: red; color: #fff"
                  v-if="state.customerOrder.type"
                  >{{ unpaid_pickup }}</span
                >
              </p>
            </div>
            <div v-if="!smAndSmaller">
              <p :class="smAndSmaller ? 'text-lg' : 'text-2xl'">
                Name:
                {{
                  state?.customerOrder?.customer?.calculated_name ||
                  state?.customerOrder?.single_customer?.calculated_name
                }}
              </p>
            </div>
            <div class="flex flex-wrap items-start">
              <div :class="smAndSmaller ? 'col-4' : 'col-2 mr-2'">
                <Button
                  :label="isRental ? 'Open Current Invoice' : 'Open Invoice'"
                  :class="
                    smAndSmaller
                      ? 'p-button-primary p-button-sm text-sm ml-4'
                      : 'p-button-primary text-lg ml-4'
                  "
                  @click="openPaymentPage"
                />
              </div>
              <div :class="smAndSmaller ? 'col-4' : 'col-3'" class="ml-6">
                <Button
                  :label="isRental ? 'Email Current Invoice' : 'Email Invoice'"
                  :class="
                    smAndSmaller
                      ? 'p-button-secondary p-button-sm text-sm ml-4'
                      : 'p-button-secondary p-button-sm text-lg ml-4'
                  "
                  :loading="state.resendInvoiceLoading"
                  @click="resendInvoice"
                />
              </div>
              <div
                :class="smAndSmaller ? 'col-12' : 'col-4'"
                v-if="state.customerOrder.type == 'RENT_TO_OWN'"
              >
                <Button
                  label="Convert to Purchase"
                  :loading="state.convertToPurchaseLoading"
                  :class="
                    smAndSmaller
                      ? 'p-button-primary p-button-sm text-sm ml-4'
                      : 'p-button-primary text-lg ml-4'
                  "
                  @click="convertToPurchase()"
                />
              </div>
              <div
                :class="
                  smAndSmaller || state.can_pay_on_delivery
                    ? 'col-2 ml-1'
                    : 'col-1 ml-3'
                "
                v-if="$ability.can('delete', 'delete_orders')"
              >
                <Button
                  type="button"
                  icon="pi pi-trash text-sm"
                  @click="deleteOrder($event)"
                  :loading="state.deleteLoading"
                  class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
                ></Button>
              </div>
              <div
                :class="
                  $ability.can('delete', 'delete_orders') ||
                  state.can_pay_on_delivery
                    ? 'col-2 ml-2'
                    : 'col-2 ml-5'
                "
              >
                <Button
                  type="button"
                  icon="pi pi-refresh"
                  @click="forceRefreshOrder($event)"
                  :loading="state.globalRefreshLoading"
                  class="w-8 h-8 p-button-rounded p-button-text bg-200 dark:bg-600 text-700 dark:text-100"
                ></Button>
              </div>
            </div>
          </div>
        </template>
        <CustomerOrderDetail
          :swap-customer-order="swapCustomerOrder"
          :openDialog="openOrderDetailDialog"
        />
      </Dialog>
      <Dialog
        v-model:visible="state.createOrderDialog"
        dismissableMask
        closeOnEscape
        :breakpoints="{
          '2000px': '55vw',
          '1400px': '65vw',
          '1200px': '75vw',
          '992px': '85vw',
          '600px': '100vw',
          '480px': '100vw',
          '320px': '100vw'
        }"
        :modal="true"
      >
        <template #header>
          <div class="flex items-stretch">
            <div class="flex">
              <p class="text-3xl">Create Invoice</p>
            </div>
          </div>
        </template>
        <create-invoice :stepsEnabled="false"></create-invoice>
      </Dialog>
      <Dialog
        v-model:visible="state.containerReleaseInfoDialog"
        closeOnEscape
        :modal="true"
      >
        <div class="col-span-12">
          <Tag
            value="Open In Inventory"
            @click="openSelectContainer(state.selectedInventory.id)"
          />
        </div>
        <div class="col-span-12">
          Release:
          {{ state.selectedInventory.container_release_number }}
        </div>
        <div class="col-span-12">
          Container number:
          {{ state.selectedInventory.container_number }}
        </div>
        <div class="col-span-12">
          Depot Name: {{ state.selectedInventory.depot.name }}
        </div>
        <div class="col-span-12">
          Depot Addr: {{ state.selectedInventory.depot.full_address }}
        </div>
        <div class="col-span-12">
          Depot Phone:
          {{ state.selectedInventory.depot.primary_phone }}
        </div>
        <div class="col-span-12">
          Depot Email:
          {{ state.selectedInventory.depot.primary_email }}
        </div>
        <div class="col-span-12">
          Vendor Name: {{ state.selectedInventory.vendor.name }}
        </div>
        <div class="col-span-12">
          Vendor Phone:
          {{ state.selectedInventory.vendor.primary_phone }}
        </div>
        <div class="col-span-12">
          Vendor Email:
          {{ state.selectedInventory.vendor.primary_email }}
        </div>
      </Dialog>
    </div>
  </div>
</template>

<script setup>
  import {
    reactive,
    computed,
    watch,
    onMounted,
    inject,
    ref,
    onBeforeMount
  } from "vue"

  import { FilterMatchMode } from "@primevue/core/api"
  import CustomerService from "@/service/Customers"
  import CustomerApi from "@/api/customers"
  import LineItemApi from "@/api/lineItem"
  import DriversService from "@/service/Drivers"
  import DriverApi from "@/api/drivers"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"
  import PricingService from "@/service/Pricing"
  import PricingApi from "@/api/pricing"
  import StatusHeader from "./StatusHeader.vue"

  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useCustomerOrderFull } from "@/store/modules/customerOrderFull"

  import { useDrivers } from "@/store/modules/drivers"
  import { useUsers } from "@/store/modules/users"
  import { useContainerPrices } from "@/store/modules/pricing"

  import LoadingTable from "../loadingTable/LoadingTable.vue"
  import CustomerOrderDetail from "./CustomerOrderDetail.vue"
  import CreateInvoice from "./create/CreateInvoice.vue"
  import NoteDetail from "../notes/NoteDetail.vue"
  import SearchFilterTable from "./SearchFilterTable.vue"

  import { useAuth0 } from "@auth0/auth0-vue"

  import { useToast } from "primevue/usetoast"
  import { breakpointsTailwind, set, useBreakpoints } from "@vueuse/core"
  import { storeToRefs } from "pinia"
  import currentRouteStatus from "../../utils/routes"

  import { useRoute } from "vue-router"
  import { useRouter } from "vue-router"
  import Lock from "../../service/Lock.js"
  import toCapitalizedWithSpaces from "../../utils/toCapitalizedWithSpaces"

  import toCamelCase from "@/utils/toCamelCase"
  import cloneDeep from "lodash.clonedeep"
  import { isRentalsVisible } from "../../utils/allowedVisibilityForFeatures"
  import { dfl, dfc, dfs } from "@/service/DateFormat.js"
  import { useConfirm } from "primevue/useconfirm"
  import { usesSwitchToOrdersHelper } from "@/store/modules/switchToOrdersHelper"
  import { useInvoiceHelper } from "@/store/modules/invoiceHelper"
  import LogisticsZonesApi from "@/api/logistics_zones"

  const invoiceHelperStore = useInvoiceHelper()

  const switchToOrdersHelper = usesSwitchToOrdersHelper()

  const confirm = useConfirm()

  const logisticsZonesApi = new LogisticsZonesApi()

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")

  const toast = useToast()
  const driverStore = useDrivers()
  const usersStore = useUsers()
  const customersStore = useCustomerOrder()
  const containerPriceStore = useContainerPrices()
  const customerStoreMergedOrders = useCustomerOrderFull()
  const $fc = inject("$formatCurrency")

  const driversService = new DriversService()
  const driverApi = new DriverApi()
  const usersService = new UsersService()
  const userApi = new UserApi()
  const customerService = new CustomerService()
  const customerApi = new CustomerApi()
  const lineItemApi = new LineItemApi()
  const pricingService = new PricingService()
  const pricingApi = new PricingApi()

  const { user } = useAuth0()

  const $DateTime = inject("$DateTime")
  const $ability = inject("$ability")
  const $fp = inject("$formatPhone")
  const $route = inject("$route")

  const largerThanSm = breakpoints.greater("sm")
  const lgAndSmaller = breakpoints.smallerOrEqual("lg")
  const greaterOrEqualLarge = breakpoints.isGreaterOrEqual("lg")

  const route = useRoute()
  const router = useRouter()

  const containerStoreLocationsLock = new Lock()

  function transformOrder(order) {
    const address_split = order.address?.full_address.split(",")

    let state = ""
    let zipCode = ""
    let address = ""
    let city = ""

    if (address_split != undefined && address_split.length >= 1) {
      state = address_split[address_split.length - 1]?.trim().split(" ")[0]
      zipCode = address_split[address_split.length - 1]?.trim().split(" ")[1]
      city = address_split[address_split.length - 2]?.trim()
      address = address_split.slice(0, address_split.length - 2).join(" | ")
    }
    return {
      order_id: order.display_order_id,
      created: dfs(order.created_at),
      date_paid: dfs(order.paid_at),
      date_delivered: dfs(order.calculated_delivered_at),
      date_completed: dfs(order.completed_at),
      "First Name": order.customer?.first_name,
      "Last Name": order.customer?.last_name,
      phone: order.customer?.phone,
      has_accessories: order.has_accessories,
      has_containers: order.has_containers,
      Agent: order.user?.full_name,
      Email: order.customer?.email,
      "CU City": order.customer?.city,
      "Total Paid": order.total_paid,
      "Line Item Length": order.line_item_length,
      "Is Pickup": order.is_pickup,
      "Calculated Profit": order.calculated_profit,
      "Container Cost": order.calculated_container_cost,
      "Shipping Cost": order.calculated_shipping_cost,
      "Calculated Gateway Cost": order.calculated_gateway_cost,
      "Calculated Total Price": order.calculated_total_price,
      "Calculated Sub Total Price": order.calculated_sub_total_price,
      "Calculated Remaining Order Balance":
        order.calculated_remaining_order_balance,
      "Calculated Misc Costs": order.calculated_misc_costs,
      "Calculated Fees": order.calculated_fees,
      "Calculated Monthly Owed Total": order.calculated_monthly_owed_total,
      "Calculated Shipping Revenue Total":
        order.calculated_shipping_revenue_total,
      "Calculated Order Tax": order.calculated_order_tax,
      "Calculated Fees Without Bank Fee":
        order.calculated_fees_without_bank_fee,
      "Calculated Monthly Subtotal": order.calculated_monthly_subtotal,
      // "current_rent_period":    order.current_rent_period,
      "Calculated discount": order.calculated_discount,
      "Calculated Vendor Names": order.calculated_vendor_names,
      "Calculated Line Items Title": order.calculated_line_items_title,
      "Calculated Paid Successfully By Credit Card":
        order.calculated_paid_successfully_by_credit_card,
      "Payment Type": order.payment_type,
      "Delivery Address": address,
      "Delivery City": city,
      "Delivery State": state,
      "Delivery Zipcode": zipCode
      //"Warehouse location": order.line_items.length > 0 ? order.line_items[0].location?.replace(',', ' |') : ''
    }
  }

  const application = computed(() => {
    return customersStore.order?.application_response?.response_content || null
  })

  const forceRefreshOrder = async (event) => {
    customersStore.setForceRefresh(true)
    state.globalRefreshLoading = true
    await getOrderByDisplayId(state.customerOrder.display_order_id)
    await swapCustomerOrder(state.customerOrder.id)
    state.globalRefreshLoading = false
    // await globalRefresh();
  }

  const deleteOrder = async (event) => {
    confirm.require({
      target: event.currentTarget,
      message:
        "Are you sure you want to delete this order? This action can not be reveresed",
      icon: "pi pi-info-circle",
      acceptClass: "p-button-danger p-button-sm",
      accept: async () => {
        state.deleteLoading = true
        const { data, error } = await customerApi.deleteOrder(
          state.customerOrder.id
        )
        if (error.value) {
          toast.add({
            severity: "error",
            summary: "Error",
            detail: error.value?.response?.data?.detail
              ? error.value.response.data.detail
              : "Error deleting order",
            group: "br",
            life: 5000
          })
          state.deleteLoading = false
          return
        }
        customersStore.setForceRefresh(true)

        if (
          state.customerOrder.status == "Delinquent" ||
          state.customerOrder.status == "Delivered"
        ) {
          let propriety_name = toCamelCase(`On Rent Orders`)
          const setter = toCamelCase(`set ${propriety_name}`)
          let allOrdersStatus = customersStore[propriety_name]
          allOrdersStatus = allOrdersStatus.filter(
            (obj) => obj.order_id != state.customerOrder.id
          )
          customersStore[setter](allOrdersStatus)
        }

        let propriety_name = toCamelCase(`${state.customerOrder.status} Orders`)
        const setter = toCamelCase(`set ${propriety_name}`)
        let allOrdersStatus = customersStore[propriety_name]
        allOrdersStatus = allOrdersStatus.filter(
          (obj) => obj.order_id != state.customerOrder.id
        )
        customersStore[setter](allOrdersStatus)

        if (state.quickSearchOrder.length > 0) {
          const line_items = state.customerOrder.line_items
          line_items.forEach((el) => {
            let index = state.quickSearchOrder.findIndex(
              (item) => el.id === item.line_item_id
            )
            state.quickSearchOrder.splice(index, 1)
          })
        }

        //await globalRefresh();
        state.updateOrderDialog = false

        toast.add({
          severity: "success",
          summary: "Success",
          detail: "Container order",
          group: "br",
          life: 5000
        })
        state.deleteLoading = false
      },
      reject: () => {
        toast.add({
          severity: "error",
          summary: "Canceled",
          detail: "Order removal canceled",
          group: "br",
          life: 2000
        })
        state.deleteLoading = false
      }
    })
  }
  const currentStatusComp = computed(() => {
    return route.query.status
  })

  const convertToPurchase = async () => {
    state.convertToPurchaseLoading = true
    const { data, isLoading, error } = await customerApi.convertToPurchase(
      state.customerOrder.id
    )

    if (error.value) {
      state.convertToPurchaseLoading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error converting order from RENT_TO_OWN to PURCHASE.",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.convertToPurchaseLoading = false
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Success converting order from RENT_TO_OWN to PURCHASE.",
        group: "br",
        life: 5000
      })
    }
  }

  const can_pay_on_delivery = async () => {
    if (!customersStore.order || customersStore.order?.type != "PURCHASE") {
      state.can_pay_on_delivery_order = false
      return
    }
    const cms_pay_on_deliver = usersStore.cms?.pay_on_delivery_contract
    if (cms_pay_on_deliver && cms_pay_on_deliver.is_enabled) {
      customerOrderStore.publicOrder?.line_items?.filter(async (e) => {
        if (cms_pay_on_deliver.max_allowed_miles >= (e.potential_miles || 0)) {
          let requestData = {
            product_name: e.title,
            location_name: e.product_city
          }
          const { data } = await customerApi.is_pay_on_delivery(requestData)
          state.can_pay_on_delivery_order =
            state.can_pay_on_delivery_order || data.value
        }
      })
    } else {
      state.can_pay_on_delivery_order = false
    }
  }

  const unpaid_pickup = computed(() => {
    if (usersStore.cms?.uses_downpayment_note) {
      return ""
    }
    let note = state.customerOrder.note.filter((e) => {
      return e.title == "downpayment_note"
    })
    return note.length > 0 ? note[0].content : ""
  })

  const tableWidth = computed(() => {
    if (greaterOrEqualLarge.value) {
      return "95vw"
    } else if (lgAndSmaller.value) {
      return "95vw"
    } else if (largerThanSm.value) {
      return "92vw"
    }
  })

  const isRental = computed(() => {
    return state.customerOrder.type == "RENT"
  })

  const nameField = (data) => {
    let name = data.customer_full_name || data.customer_company_name

    if (data.order_single_customer) {
      name =
        `${data.order_single_customer.first_name} ${data.order_single_customer.last_name}` ||
        data.order_single_customer.company_name
    }

    return name
  }

  const getCustomerPhone = (data) => {
    return data.order_single_customer != null
      ? $fp(data.order_single_customer?.customer_contacts[0].phone)
      : $fp(data.customer_phone)
  }

  const getCustomerEmail = (data) => {
    return data.order_single_customer != null
      ? data.order_single_customer?.customer_contacts[0].email
      : data.customer_email
  }

  const getSignedDate = (data) => {
    return dfc(data.order_calculated_signed_date) != "Invalid DateTime"
      ? dfc(data.order_calculated_signed_date)
      : ""
  }

  const openOrderDetailDialog = async (display_order_id) => {
    state.updateOrderDialog = false

    await getOrderByDisplayId(display_order_id)

    const currentParams = { ...route.params }
    currentParams.id = display_order_id
    state.prevent_route_load = true
    router.push({ name: "invoices_with_id", params: currentParams })
    state.submitted = false
    state.updateOrderDialog = true
  }

  const camelCasedOrderStatus = computed(() => {
    if (!route.query.status) {
      return
    }
    return toCamelCase(
      route.query.status.replace(/_/g, " ").toLowerCase() + "Orders"
    )
  })

  const filteredCustomerOrders = computed(() => {
    if (state.quickSearchOrder && state.quickSearch) {
      state.quickSearchOrder.map((el) => {
        el.order_calculated_paid_date_rental =
          dfc(el.order_calculated_paid_date_rental) != "Invalid DateTime"
            ? dfc(el.order_calculated_paid_date_rental)
            : el.display_paid_at
        el.order_signed_at =
          dfc(el.order_signed_at) != "Invalid DateTime"
            ? dfc(el.order_signed_at)
            : el.display_signed_at
      })
      customerStoreMergedOrders.setDisplayOrderIds(
        state.quickSearchOrder.map((o) => {
          return o.order_display_order_id
        })
      )
      return state.quickSearchOrder
    }
    if (state.searchAndFilter) {
      customerStoreMergedOrders.setDisplayOrderIds(
        customersStore.searchedOrders.map((o) => {
          return o.order_display_order_id
        })
      )
      return customersStore.searchedOrders
    } else {
      if (
        !customersStore[camelCasedOrderStatus.value] ||
        customersStore[camelCasedOrderStatus.value]?.length === 0
      ) {
        console.log("no customers in store")
        state.refreshKey += 1
        return []
      }
      state.customers = cloneDeep(
        customersStore[camelCasedOrderStatus.value]
      ).filter((e) => {
        if (state.selectedCategory.product_type === "ALL") return true
        if (
          state.selectedCategory.product_type === "CONTAINER_ACCESSORY" &&
          !e.order_has_accessories
        )
          return false
        if (
          state.selectedCategory.product_type === "SHIPPING_CONTAINER" &&
          !e.order_has_containers
        )
          return false
        return true
      })
      if (state.customers?.length === 0) {
        return []
      }
      customerStoreMergedOrders.setDisplayOrderIds(
        state.customers.map((o) => {
          return o.order_display_order_id
        })
      )

      if (isRentalsFeatureVisible.value) {
        return state.customers?.filter(
          (c) =>
            c?.order_type &&
            (c.order_type === state.selectedCategory.code ||
              state.selectedCategory.code === "ALL")
        )
      }

      return state.customers
    }
  })

  const colorRows = () => {
    let pairs = [
      { class_name: "ZoneA", name: "A" },
      { class_name: "ZoneB", name: "B" },
      { class_name: "ZoneC", name: "C" }
    ]

    pairs.forEach((pair) => {
      let zoneElements = document.querySelectorAll("." + pair["class_name"])
      state.logistics_zones.forEach((el) => {
        if (el.zone_name == pair["name"]) {
          zoneElements.forEach((zoneEl) => {
            zoneEl.style.backgroundColor = el.color
          })
        }
      })
    })
  }

  const openSelectContainer = (id) => {
    const currentParams = { ...route.params }
    currentParams.id = id.slice(0, 4)
    router.push({ name: "inventory_with_id", params: currentParams })
  }

  const categories = computed(() => {
    let data = isRentalsFeatureVisible.value
      ? [
          { name: "All", code: "ALL", product_type: "ALL" },
          {
            name: "Container Sales",
            code: "PURCHASE",
            product_type: "SHIPPING_CONTAINER"
          },
          { name: "Rentals", code: "RENT", product_type: "ALL" }
        ]
      : []

    if (
      usersStore.cms?.feature_flags?.rto_enabled == true ||
      usersStore.cms?.feature_flags?.rto_enabled == null
    ) {
      data.push({
        name: "Rent to Own",
        code: "RENT_TO_OWN",
        product_type: "ALL"
      })
    }
    if ($ability.can("view", "accessories")) {
      data.push({
        name: "Accessory Sales (Old)",
        code: "PURCHASE",
        product_type: "CONTAINER_ACCESSORY"
      })
      data.push({
        name: "Accessory Sales",
        code: "PURCHASE_ACCESSORY",
        product_type: "CONTAINER_ACCESSORY"
      })
    }
    return data
  })

  const isRentalsFeatureVisible = computed(() => {
    let isProd = import.meta.env.PROD
    let accountId = usersStore?.cms?.account_id
    let isCMSRentalsEnabled = usersStore.cms?.feature_flags?.rentals_enabled
    let userEmail = usersStore?.currentUser?.email
    let isRentalsFeatureVisible = isRentalsVisible(
      isProd,
      accountId,
      isCMSRentalsEnabled,
      userEmail
    )

    return isRentalsFeatureVisible
  })

  const filteredColumns = computed(() => {
    let columnOrdering
    if (state.selectedCategory.code == "RENT") {
      columnOrdering =
        usersStore.currentUser?.preferences?.rent
          ?.invoice_table_column_ordering ||
        customerService.columnOrdering($ability.can)

      columnOrdering.forEach((element) => {
        element.exceptOrderType = []
      })
    } else if (
      state.selectedCategory.code == "PURCHASE" ||
      state.selectedCategory.code == "PURCHASE_ACCESSORY"
    ) {
      columnOrdering =
        usersStore.currentUser?.preferences?.purchase
          ?.invoice_table_column_ordering ||
        customerService.columnOrdering($ability.can)
    } else if (state.selectedCategory.code == "RENT_TO_OWN") {
      columnOrdering =
        usersStore.currentUser?.preferences?.rent_to_own
          ?.invoice_table_column_ordering ||
        customerService.columnOrdering($ability.can)
    } else if (state.selectedCategory.code == "ALL") {
      columnOrdering =
        usersStore.currentUser?.preferences?.all
          ?.invoice_table_column_ordering ||
        customerService.columnOrdering($ability.can)
    }

    let status =
      state.searchAndFilter || state.quickSearchOrder.length
        ? "Search&Filter"
        : currentStatusComp.value || "Invoiced"
    status = toCapitalizedWithSpaces(status)
    return columnOrdering
      .filter((c) => {
        if (c?.except?.includes(status)) return false
        if (c?.exceptOrderType?.includes(state.selectedCategory.code)) {
          return false
        }
        return (
          c.showOnStatus[0] === "All" ||
          c.showOnStatus.some((s) => {
            return s.toLowerCase() === status.toLowerCase()
          })
        )
      })
      .filter((o) => o?.allowed)
  })

  const sortField = computed(() => {
    if (currentStatusComp.value?.toLowerCase() === "invoiced") {
      return "order_created_at"
    }
    if (currentStatusComp.value?.toLowerCase() === "expired") {
      return "order_created_at"
    }
    if (currentStatusComp.value?.toLowerCase() === "paid") {
      return "order_paid_at"
    }
    if (currentStatusComp.value?.toLowerCase() === "delivered") {
      return "order_calculated_delivered_at"
    }
    if (currentStatusComp.value?.toLowerCase() === "completed") {
      return "order_completed_at"
    }
    if (currentStatusComp.value?.toLowerCase() === "to_deliver") {
      return "order_paid_at"
    }
    return "order_created_at"
  })

  const driversList = computed(() => {
    return driverStore.drivers
      .map((d) => {
        return { label: d.company_name, value: d.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const state = reactive({
    customers: [],
    forceRefresh: false,
    quickSearch: "",
    deliveryNoteLoading: false,
    ordersRaw: [],
    quickSearchOrder: [],
    containerReleaseInfoDialog: false,
    lastPage: false,
    quickSearchLoading: false,
    individualOrderLoading: false,
    refreshKey: 0,
    selectedAddButton: null,
    loadingLineItem: null,
    searchAndFilter: false,
    offlineModeLoading: false,
    loading: false,
    resendInvoiceLoading: false,
    sendPaymentOnDelivery: false,
    convertToPurchaseLoading: false,
    loadingSavePreferences: false,
    loadingResetColumnOrdering: false,
    selectedColumns: [],
    customerRawLength: 0,
    resultCount: 0,
    createOrderDialog: false,
    updateOrderDialog: false,
    noteDialog: false,
    customerOrder: {},
    selectedProducts: null,
    filters: {},
    submitted: false,
    globalRefreshLoading: false,
    selectedStatusIndex: 0,
    selectedInventory: null,
    copiedText: "",
    switchSteps: true,
    offlineMode: false,
    exportOrders: false,
    selectedCategory: { name: "All", code: "ALL", product_type: "ALL" },
    loaded_once_with_param: false,
    prevent_route_load: false,
    previous_route_status: undefined,
    deleteLoading: false,
    logistics_zones: [],
    can_pay_on_delivery_order: false
  })

  const dt = ref()

  const initFilters = () => {
    state.filters = {
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    }
  }

  initFilters()

  const buttonClass = (slotProps, col) => {
    if (slotProps?.data?.order_note) {
      if (usersStore.darkMode) {
        return slotProps.data?.order_note?.length > 0
          ? "p-button-rounded p-button-primary"
          : "p-button-rounded p-button-info"
      } else {
        return slotProps.data?.order_note?.length > 0
          ? "p-button-rounded p-button-primary"
          : "p-button-rounded p-button-secondary"
      }
    }

    return usersStore.darkMode
      ? "p-button-rounded p-button-primary font-large text-md"
      : "p-button-rounded p-button-secondary font-large text-md"
  }

  const quickSearch = async (keyPressEvent) => {
    if (keyPressEvent && keyPressEvent.key !== "Enter") {
      return
    }
    state.customers = []
    state.loading = false
    state.quickSearchLoading = true
    const { data, error } = await customerApi.getOrderByDisplayId(
      state.quickSearch
    )

    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: error.value.response.data.detail,
        group: "br",
        life: 5000
      })
      state.quickSearchLoading = false
      return
    }

    if (data.value.length === 0) {
      toast.add({
        severity: "info",
        summary: "Info",
        detail: "No customers found",
        group: "br",
        life: 5000
      })
      state.quickSearchLoading = false
      return
    }
    console.log(data.value)
    customerStoreMergedOrders.mergeOrders([data.value])
    state.quickSearchOrder = await customerService.dtoOrder([data.value])
    console.log(state.quickSearchOrder)
    state.quickSearchLoading = false
  }

  const copyColumnToClipboard = ($event, lineItemId, columnName) => {
    let textToCopy = ""
    if (
      columnName.includes("container_release") ||
      columnName.includes("container_number")
    ) {
      const found = filteredCustomerOrders.value.find(
        (c) => c.line_item_id === lineItemId
      )
      if (!found.line_item_inventory_container_release_number) {
        console.log("container not found")
        return
      }
      state.selectedInventory = found.line_item_inventory
      textToCopy = `${found.line_item_inventory.container_release_number} \n ${found.line_item_inventory.depot.full_address}`
      const depotContact = `Depot Contact: ${found.line_item_inventory.depot.name} | ${found.line_item_inventory.depot.primary_phone} ${found.line_item_inventory.depot.primary_email}`
      const vendorContact = `Vendor Contact: ${found.line_item_inventory.vendor.name} | ${found.line_item_inventory.vendor.primary_phone} ${found.line_item_inventory.vendor.primary_email}`
      textToCopy = `${textToCopy} \n ${depotContact} \n ${vendorContact}`
    }
    state.copiedText = textToCopy
    if (textToCopy === "") {
      return
    }
    state.containerReleaseInfoDialog = true
  }

  const globalRefresh = async () => {
    state.quickSearch = ""
    state.globalRefreshLoading = true

    await refreshUsers(false)
    const { data } = await driverApi.getDrivers(false)
    driverStore.setDrivers(data.value)

    await customerApi.refreshCache()
    await getCustomers(0, true)

    state.globalRefreshLoading = false
  }

  const onNoteSubmitted = async (orderId) => {
    console.log("onNoteSubmitted", orderId)
    if (orderId) {
      let routeStatus = currentRouteStatus($route)
      await customerService.swapCustomerOrder(orderId, routeStatus)
    }
    state.noteDialog = false
    state.refreshKey++
  }

  const displayField = (data, field) => {
    if (Array.isArray(data[field]) && data[field].length > 0) {
      return data[field][data[field].length - 1]?.content
    } else if (!Array.isArray(data[field]) && data[field]) {
      return data[field].toString()
    } else {
      return "Add"
    }
  }

  const loadDriversList = async (currentCol) => {
    if (driverStore.drivers.length === 0 && currentCol.includes("driver")) {
      const { data } = await driverApi.getDrivers()
      const drivers = data.value.map((l) => driversService.dtoDriver(l))
      driverStore.setDrivers(drivers)
    }
  }

  const getCustomers = async (
    skip = 0,
    force = $route.currentRoute.value.query.forceRefresh,
    multipleRequests = false
  ) => {
    let currentStatus = route.query.status
    if (currentStatus == undefined) {
      currentStatus = "invoiced"
    }

    let camelCasedOrderStatus = toCamelCase(
      currentStatus.replace(/_/g, " ").toLowerCase() + "Orders"
    )

    if (state.lastPage) {
      return
    }
    if (skip === 0) {
      state.customers = []
    }

    await containerStoreLocationsLock.acquire()
    if (
      containerPriceStore.locations.length === 0 &&
      usersStore.cms?.feature_flags?.order_row_coloring
    ) {
      return
    }
    await containerStoreLocationsLock.release()

    state.customers = []
    console.log(force, "force")

    if (
      customersStore[camelCasedOrderStatus]?.length > 0 &&
      skip === 0 &&
      !force &&
      !multipleRequests
    ) {
      state.customers = customersStore[camelCasedOrderStatus]
      return
    }

    state.loading = true
    const { data, error } = await customerApi.getCustomersByStatus(
      currentStatus,
      state.selectedCategory.code,
      usersStore.isEmulating ? usersStore.currentUser.id : null,
      state.selectedCategory.product_type,
      skip,
      multipleRequests
    )

    if (error.value) {
      state.loading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading customers",
        group: "br",
        life: 5000
      })
      return
    }

    if (data.value.orders.length === 0 && skip > 0) {
      console.log("no more customers")
      state.loading = false
      state.lastPage = true
    }

    customerStoreMergedOrders.mergeOrders(data.value.orders)

    if (data.value.orders.length > 0 && !multipleRequests) {
      state.customerRawLength += data.value.orders.length
      if (skip == 0 && force == true) {
        await customerService.resetOrders(currentStatus)
      }
      await customerService.setOrders(data.value.orders, currentStatus)
      state.resultCount = data.value.count
      state.customers = customersStore[camelCasedOrderStatus]
      state.loading = false
    }

    if (data.value.orders.length > 0 && multipleRequests) {
      await containerStoreLocationsLock.acquire()
      state.customerRawLength += data.value.orders.length
      state.resultCount = data.value.count
      state.ordersRaw = [...state.ordersRaw, ...data.value.orders]
      await containerStoreLocationsLock.release()
    }

    if (!multipleRequests) {
      state.loading = false
    }
  }

  const getOrderByDisplayId = async (id) => {
    const { data, error } = await customerApi.getOrderByDisplayId(id)
    if (error.value) {
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error loading order",
        group: "br",
        life: 5000
      })
      return false
    }
    if (data) {
      state.customerOrder = data.value
      customersStore.setOrder(data.value)
      customersStore.setApplyDiscount(data.value.is_discount_applied)
    }
    return true
  }

  const openPaymentPage = () => {
    // get calculated current rent period id

    if (state.customerOrder.type == "RENT") {
      const rent_period_id = state.customerOrder.current_rent_period.id

      if (import.meta.env.DEV) {
        let url = `${import.meta.VITE_APP_PAYMENT_URL}/#/rental_invoice/${
          state.customerOrder.id
        }/${rent_period_id}`
        window.open(url, "_blank")
        return
      }

      if (import.meta.env.PROD) {
        let invoice_email_link = usersStore.cms?.links?.invoice_email_link
        let url =
          invoice_email_link +
          `rental_invoice/${state.customerOrder.id}/${rent_period_id}`
        window.open(url, "_blank")
        return
      }
    }

    let url
    if (import.meta.env.PROD) {
      let invoice_email_link = usersStore.cms?.links?.invoice_email_link
      let url = invoice_email_link + `${state.customerOrder.id}`

      window.open(url, "_blank")
      return
    }

    if (import.meta.env.DEV) {
      url = `${import.meta.VITE_APP_PAYMENT_URL}/#/payment/${
        state.customerOrder.id
      }`

      window.open(url, "_blank")
      return
    }
  }

  const resendInvoice = async () => {
    state.resendInvoiceLoading = true
    const { data, isLoading, error } = await customerApi.resendInvoice(
      state.customerOrder.id
    )

    if (error.value) {
      state.resendInvoiceLoading = false
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error resending invoice",
        group: "br",
        life: 5000
      })
      return
    }

    if (data) {
      state.resendInvoiceLoading = false
      toast.add({
        severity: "success",
        summary: "Success",
        detail: "Invoice resent",
        group: "br",
        life: 5000
      })
    }
  }

  const emptyOrder = () => {
    const status = currentRouteStatus($route)
    customersStore.setOrder(null)
    if (status !== null) {
      router.push({ name: "invoices", query: { status: status } })
    } else {
      router.push({
        name: "invoices",
        query: { status: state.previous_route_status }
      })
    }
  }

  const openButton = async (field, data) => {
    if (field === "order_display_order_id") {
      openNew(data, field)
    }

    if (field === "order_note") {
      await getOrderByDisplayId(data.order_display_order_id)
      if (state.customerOrder) {
        state.noteDialog = true
      }
    }
  }

  const quickSearchReset = () => {
    state.quickSearch = null
    state.quickSearchOrder = []
  }

  onMounted(async () => {
    if (Object.keys($route.currentRoute.value.params).length !== 0) {
      if ($route.currentRoute.value.params.hasOwnProperty("id")) {
        const orderDisplayId = $route.currentRoute.value.params["id"]

        const order = await customerApi.getOrderByDisplayId(orderDisplayId)
        state.customerOrder = order.data.value
        customersStore.setOrder(order.data.value)
        state.updateOrderDialog = true
        state.loaded_once_with_param = true
      }
    }

    if (route.query.forceRefresh) {
      const currentParams = { ...route.query }
      currentParams.forceRefresh = false
      router.push({ query: currentParams })
      /* setTimeout(() => {
      router.go();
      // reloads the whole page, not good.
    }, 50);*/
      // router.push({ query: { forceRefresh: false } });
    }

    if (containerPriceStore.locations.length === 0) {
      await containerStoreLocationsLock.acquire()
      state.loading = true
      const { data } = await pricingApi.getLocations()
      containerPriceStore.setLocations(
        data.value.map((location) => pricingService.dtoLocation(location))
      )
      state.loading = false
      await containerStoreLocationsLock.release()
    }

    if (Object.keys($route.currentRoute.value.query).length !== 0) {
      await resetOnCustomerOrderStatusChange()
    }

    // if (
    //   Object.keys($route.currentRoute.value.query).length === 0 &&
    //   Object.keys($route.currentRoute.value.params).length !== 0
    // ) {
    //   router.push({ name: "invoices", query: { status: "invoiced" } });
    // }
    const { data } = await driverApi.getDrivers()
    const drivers = data.value.map((l) => driversService.dtoDriver(l))
    driverStore.setDrivers(drivers)

    const lz_data = await logisticsZonesApi.getAllLogisticsZones()
    state.logistics_zones = lz_data.data.value
    state.logistics_zones = [...state.logistics_zones].sort((a, b) =>
      a.zone_name.localeCompare(b.zone_name)
    )

    setInterval(() => {
      colorRows()
    }, 2000)
  })

  const yesNoInProgressClass = (currentVal) => {
    if (usersStore.darkMode) {
      if (currentVal === "IN PROGRESS") {
        return "bg-orange-900"
      } else if (currentVal === "YES") {
        return "bg-green-100"
      } else {
        return "bg-red-100"
      }
    } else {
      if (currentVal === "IN PROGRESS") {
        return "bg-orange-100"
      } else if (currentVal === "YES") {
        return "bg-green-100"
      } else {
        return "bg-red-100"
      }
    }
  }

  const rowClass = (data) => {
    if (
      !usersStore.darkMode &&
      usersStore.cms?.feature_flags?.order_row_coloring
    ) {
      if (Number(data?.line_item_shipping_revenue) === 0) {
        const foundLocation = containerPriceStore.locations.find((location) =>
          data.line_item_product_city?.includes(location.city)
        )

        if (foundLocation) {
          if (foundLocation.pickup_region == "PU A") {
            return [{ "bg-blue-100": true }]
          } else if (foundLocation.pickup_region == "PU B") {
            return [{ pu_b: true }]
          } else {
            return [{ "bg-orange-100": true }]
          }
        }
      } else {
        const foundLocation = containerPriceStore.locations.find((location) =>
          data.line_item_product_city?.includes(location.city)
        )
        if (foundLocation) {
          return [
            {
              ZoneA: foundLocation.region === "A",
              ZoneB: foundLocation.region === "B",
              ZoneC: foundLocation.region === "C",
              ZoneD: foundLocation.region === "D"
            }
          ]
        }
      }
    } else {
      return null
    }
  }

  const onRowExpand = () => console.log("expand")

  const onCellEditComplete = async (e, col = null, lineItemData = null) => {
    let field = e?.field || col?.field
    field = field.replace("line_item_", "").replace("order_", "")

    let requestData = {
      [field]: col ? e?.value : e?.newValue
    }
    state.loadingLineItem = e?.data?.line_item_id || lineItemData?.line_item_id
    let data, isLoading, error

    if (field === "note") {
      requestData = {
        notes: {
          title: e.newValue,
          content: e.newValue
        }
      }
    }

    if (field === "potential_miles") {
      requestData = {
        potential_miles: e.newValue || 0
      }
    }

    if (field === "potential_dollar_per_mile") {
      requestData = {
        potential_dollar_per_mile: e.newValue || 0
      }
    }

    if (field === "scheduled_date") {
      // certain events return an object instead of a string, in which case we want to set the date to null
      if (typeof e !== "string" && !Date.parse(e)) {
        requestData = {
          scheduled_date: null
        }
      } else {
        requestData = {
          scheduled_date: $DateTime.fromJSDate(e).toISO()
        }
      }
    }

    if (field === "potential_date") {
      // certain events return an object instead of a string, in which case we want to set the date to null
      if (typeof e !== "string" && !Date.parse(e)) {
        requestData = {
          potential_date: null
        }
      } else {
        requestData = {
          potential_date: e
        }
      }
    }

    if (field === "potential_driver_id") {
      requestData = {
        potential_driver_id: e.value
      }
    }

    if (field === "driver.company_name") {
      requestData = {
        driver_id: e.value
      }
    }

    if (field === "payment_type") {
      ;({ data, isLoading, error } = await customerApi.updateOrder(
        lineItemData?.order_id,
        requestData
      ))
    } else {
      ;(requestData["id"] =
        e?.data?.line_item_id || lineItemData?.line_item_id),
        ({ data, isLoading, error } = await lineItemApi.updateLineItem([
          requestData
        ]))
    }

    if (error.value) {
      state.loading = null
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Error saving info",
        group: "br",
        life: 2000
      })
      return
    }
    if (data.value) {
      state.loadingLineItem = null
      toast.add({
        severity: "success",
        summary: "Success",
        detail: `${field} saved`,
        group: "br",
        life: 2000
      })
    }
    let order
    if (Array.isArray(data.value)) {
      order = data.value[0].order
    } else {
      order = data.value
    }
    let routeStatus = currentRouteStatus($route)
    await customerService.swapCustomerOrderLineItem(
      order.id,
      lineItemData ?? e?.data,
      routeStatus
    )
  }

  const swapCustomerOrder = async (orderId, lineItemId = null) => {
    const { data } = await customerApi.getOrderById(orderId)
    let index
    if (data.value) {
      if (lineItemId) {
        index = state.customers.findIndex(
          (item) => item.line_item_id === line_item_id
        )
      } else {
        index = state.customers.findIndex((item) => item.order_id === orderId)
      }

      if (state.customers[index] == undefined) {
        return
      }
      let old_status = state.customers[index].order_status

      state.customers[index] = await customerService.dtoOrder([data.value])[0]

      customerService.swapCustomerOrder(
        state.customers[index].order_id,
        state.customers[index].order_status,
        old_status
      )

      if (state.quickSearchOrder.length > 0) {
        if (lineItemId) {
          index = state.quickSearchOrder.findIndex(
            (item) => item.line_item_id === line_item_id
          )
        } else {
          index = state.quickSearchOrder.findIndex(
            (item) => item.order_id === orderId
          )
        }

        state.quickSearchOrder[index] = await customerService.dtoOrder([
          data.value
        ])[0]
      }
    }
    state.loadingLineItem = null
  }

  const refreshUsers = async (cached = true) => {
    const { data } = await userApi.getUsers(cached)
    usersStore.setUsers(data.value.map((u) => usersService.dtoUser(u)))
    state.refreshKey += 1
  }

  const getAllInvoices = async () => {
    const promises = []
    let i = 0
    while (i < state.resultCount) {
      promises.push(getCustomers(i, false, true))
      i += 200
    }

    state.loading = true
    await Promise.allSettled(promises)
    await customerService.setOrders(state.ordersRaw, currentStatusComp.value)
    state.loading = false
    toast.add({
      severity: "success",
      summary: "Success",
      detail: `All invoices loaded`,
      group: "br",
      life: 2000
    })
  }

  const onPage = async (props) => {
    if (
      props.page === props.pageCount - 1 &&
      !state.searchAndFilter &&
      state.resultCount !== state.customerRawLength
    ) {
      state.resultCount = await getCustomers(state.customerRawLength).count
    } else {
      return false
    }
  }

  const openNew = async (data = null, field = null) => {
    if (data && field) {
      state.individualOrderLoading = data["line_item_id"]
      const res = await getOrderByDisplayId(data[field])

      state.individualOrderLoading = null

      if (res == true) {
        state.submitted = false
        state.updateOrderDialog = true

        const currentParams = { ...route.params }
        currentParams.id = data["order_display_order_id"]
        state.prevent_route_load = true
        router.push({ name: "invoices_with_id", params: currentParams })
      }
    } else {
      state.customerOrder = {}
    }
  }

  const showTooltip = ref(false)

  function convertArrayOfObjectsToCSV(data) {
    const columns = filteredColumns.value
      .filter((el) => el.allowed)
      .map((el) => el.display)
    columns.unshift("Order Id")
    const csvHeader = columns.join(",") + "\n"

    const csvData = data
      .map((item) => {
        let res = ""
        for (var i = 0; i < columns.length; i++) {
          if (!item.hasOwnProperty(columns[i])) {
            res += ","
          } else {
            res += item[columns[i]] + ","
          }
        }
        return res
      })
      .join("\n")
    return csvHeader + csvData
  }
  function getNestedProperty(obj, path) {
    return path.split(".").reduce((acc, part) => acc && acc[part], obj)
  }

  function convertArrayOfObjectsToCSVOrders(data) {
    const csvHeader = Object.keys(data[0]).join(",") + "\n"
    const csvData = data.map((item) => Object.values(item).join(",")).join("\n")
    return csvHeader + csvData
  }

  // Function to set nested property value based on dot notation
  function setNestedProperty(obj, path, value) {
    const parts = path.split(".")
    const last = parts.pop()
    const target = parts.reduce((acc, part) => {
      if (!acc[part]) acc[part] = {}
      return acc[part]
    }, obj)
    target[last] = value
  }
  const arrayToCSV = (array) => {
    const filename = "download.csv"
    const blob = new Blob([array], { type: "text/csv;charset=utf-8;" })
    if (navigator.msSaveBlob) {
      navigator.msSaveBlob(blob, filename)
    } else {
      const link = document.createElement("a")
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob)
        link.setAttribute("href", url)
        link.setAttribute("download", filename)
        link.style.visibility = "hidden"
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }
  }
  // Function to transform object based on invoiceColumns mapping
  function transformObject(obj, columns) {
    const newObj = {}
    for (const column of columns) {
      const { field, display } = column
      const value = getNestedProperty(obj, field)
      if (value !== undefined) {
        setNestedProperty(newObj, display, value)
      }
    }
    return newObj
  }

  // Function to transform invoiceList based on invoiceColumns
  const transformInvoiceList = (invoiceList, invoiceColumns) => {
    let invoiceListCopy = cloneDeep(invoiceList)
    invoiceListCopy.forEach((el) => {
      el.order_note = undefined
      el.line_item_note = undefined
    })
    return invoiceListCopy.map((invoice) =>
      transformObject(invoice, invoiceColumns)
    )
  }
  const exportCSV = async () => {
    if (!state.exportOrders) {
      let driver_dictionary = {}
      for (var i = 0; i < driversList.value.length; i++) {
        driver_dictionary[driversList.value[i].value] =
          driversList.value[i].label
      }
      let elements = cloneDeep(filteredCustomerOrders.value)
      elements.forEach((el) => {
        if (
          driver_dictionary.hasOwnProperty(el["line_item_potential_driver_id"])
        ) {
          el["line_item_potential_driver_id"] =
            driver_dictionary[el["line_item_potential_driver_id"]]
        }
        el.order_paid_at = dfc(el.order_paid_at)
        el.display_paid_at = dfc(el.display_paid_at)
        el.order_calculated_paid_in_full_date = dfc(
          el.order_calculated_paid_in_full_date
        )
      })
      const csvContent = convertArrayOfObjectsToCSV(
        removeCommas(
          transformInvoiceList(elements, [
            { field: "order_display_order_id", display: "Order Id" },
            ...filteredColumns.value
          ])
        )
      )
      arrayToCSV(csvContent)
    } else {
      const orders = await customerApi.get_exported_orders(
        route.query.status,
        state.selectedCategory.code,
        usersStore.isEmulating ? usersStore.currentUser.id : null,
        customerStoreMergedOrders.getDisplayedOrdersIds()
      )
      const exportedOrders = orders.data.value.orders.map(transformOrder)
      const csvContent = convertArrayOfObjectsToCSVOrders(
        removeCommas(exportedOrders)
      )
      arrayToCSV(csvContent)
    }
  }
  const removeCommas = (value) => {
    if (typeof value === "string") {
      return value.replace(/,/g, "")
    }
    if (Array.isArray(value)) {
      return value.map(removeCommas)
    }
    if (typeof value === "object" && value !== null) {
      const newObj = {}
      for (const key in value) {
        if (value.hasOwnProperty(key)) {
          newObj[key] = removeCommas(value[key])
        }
      }
      return newObj
    }
    return value
  }

  const resetOnCustomerOrderStatusChange = async () => {
    state.lastPage = false
    state.customers = []
    state.ordersRaw = []
    customersStore.setForceRefresh(false)

    state.customerRawLength = 0

    await customersStore.lock.acquire()

    state.customerRawLength = 0
    await getCustomers(0)
    await customersStore.lock.release()
    state.selectedColumns = filteredColumns.value
  }

  watch(
    () => route.params,
    async (newParams, oldParams) => {
      if (
        Object.keys($route.currentRoute.value.params).length != 0 &&
        state.prevent_route_load == false
      ) {
        const orderDisplayId = $route.currentRoute.value.params["id"]
        const order = await customerApi.getOrderByDisplayId(orderDisplayId)
        state.customerOrder = order.data.value
        customersStore.setOrder(order.data.value)
        state.updateOrderDialog = true
      }
    }
  )

  watch(
    () => state.offlineMode,
    async (newVal) => {
      console.log("offline mode toggled", newVal)
      state.offlineModeLoading = true
      usersStore.setOfflineMode(newVal)

      let newPreferences = {
        preferences: {
          ...usersStore.currentUser?.preferences,
          offlineMode: state.offlineMode
        }
      }
      state.offlineModeLoading = false
    }
  )

  watch(
    () => $route.currentRoute.value.query.status,
    async (newVal, oldVal) => {
      if (newVal) {
        await resetOnCustomerOrderStatusChange()
      }
      // this code will allow us to keep track of the previous route status in the case that they
      // select an order and the route status disappears, then we can know where to go to after
      // they exit the order detail. Before it just took the order status and used that as the
      // new route param, but now in the emptyOrder() function, we are grabbing the current route
      // status and then seeing if it is null, signifying that we have wiped the status and if it
      // is null, then we grab the previous route status and use that one.
      if (oldVal) {
        state.previous_route_status = oldVal
      }
    }
  )

  watch(
    () => state.selectedCategory,
    async () => {
      await customersStore.lock.acquire()
      customersStore.setSelectedCategory(state.selectedCategory)
      state.lastPage = false
      state.selectedColumns = filteredColumns.value
      await getCustomers()
      await customersStore.lock.release()
    }
  )

  watch(
    () => state.quickSearch,
    async (newVal) => {
      if (newVal.length === 0) {
        state.quickSearchOrder = []
      }
    },
    { deep: true }
  )

  watch(
    () => switchToOrdersHelper.index,
    async (newVal) => {
      state.searchAndFilter = false
    }
  )

  watch(
    () => state.searchAndFilter,
    async (newVal) => {
      if (!newVal) {
        customersStore.setSearchedOrders([])
      }
    }
  )

  const entireStore = storeToRefs(customersStore)
  watch(
    () => entireStore,
    async (newVal) => {
      state.refreshKey = Math.random()
    },
    { deep: true, immediate: true }
  )

  watch(
    () => state.updateOrderDialog,
    async (oldValue, newValue) => {
      if (oldValue == false && newValue == true) {
        console.log("In")
        if (
          usersStore.cms?.feature_flags?.notes_reminder &&
          $ability.can("read", "see_notes_reminder")
        ) {
          console.log("Out")
          toast.add({
            severity: "warn",
            summary: "Quick reminder",
            detail: `Have you added notes to this order?`,
            position: "bottom-center",
            group: "bc",
            life: 9999
          })
        }
        if (state.loaded_once_with_param == true) {
          state.loaded_once_with_param = false

          if (containerPriceStore.locations.length === 0) {
            state.loading = true
            const { data } = await pricingApi.getLocations()
            containerPriceStore.setLocations(
              data.value.map((location) => pricingService.dtoLocation(location))
            )
          }
          await getCustomers()
        }
      }
    }
  )

  watch(
    () => route.query.forceRefresh,
    async (oldValue, newValue) => {
      if (newValue == true) {
        await resetOnCustomerOrderStatusChange()
      }
    }
  )

  watch(
    () => state.updateOrderDialog,
    async (oldValue, newValue) => {
      if (newValue == true) {
        await can_pay_on_delivery()
      } else {
        state.can_pay_on_delivery_order = false
      }
    }
  )

  watch(
    () => invoiceHelperStore.hideOrderDetails,
    async (oldValue, newValue) => {
      state.updateOrderDialog = false
      await customersStore.lock.acquire()
      await getCustomers(0, true)
      await customersStore.lock.release()
    }
  )
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

  .export-orders-switch {
    margin-right: 20px;
  }

  .label-input-switch {
    margin-right: 10px;
  }

  .export-switch-container {
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: end;
    width: 200px;
  }

  .tooltip {
    position: absolute;
    background-color: #333;
    color: #fff;
    padding: 5px 10px;
    border-radius: 5px;
    z-index: 999;
    top: -80px;
    left: 30px;
  }

  ::v-deep(.editable-cells-table td.p-cell-editing) {
    padding-top: 0;
    padding-bottom: 0;
  }

  .align-right {
    text-align: right;
    justify-content: center;
  }

  .align-center {
    text-align: center;
  }

  // .p-datatable th[class*="align-"] .p-column-header-content {
  //   display: inline-flex ;
  // }
  .categories-button button {
    margin-left: 5px;
    font-size: 14px !important;
    padding: 11px 20px !important;
  }

  @media screen and (max-width: 960px) {
    ::v-deep(.p-toolbar) {
      flex-wrap: wrap;

      .p-button {
        margin-bottom: 0.25rem;
      }
    }
  }
</style>
<style>
  .p-toolbar-start {
    overflow-x: scroll;
    max-width: 95vw;
  }

  .pu_b {
    background-color: #a3a3a3;
  }
</style>
