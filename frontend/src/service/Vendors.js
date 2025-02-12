import { useHttp } from "@/composables/useHttp"
import { dfl } from "@/service/DateFormat"

export default class VendorsService {
  dtoVendor(vendor) {
    return Object.assign({}, vendor, {
      created_at: dfl(vendor.created_at),
      modified_at: dfl(vendor.modified_at)
    })
  }

  columnOrdering = [
    {
      field: "created_at",
      display: "Created",
      sortable: true,
      style: "max-width: 120px"
    },
    {
      field: "modified_at",
      display: "Modified",
      sortable: true,
      style: "max-width: 120px"
    },
    {
      field: "name",
      display: "Name",
      sortable: true,
      style: "max-width: 120px"
    },
    {
      field: "address",
      display: "Address",
      sortable: true,
      style: "max-width: 160px"
    },
    {
      field: "city",
      display: "City",
      sortable: true,
      style: "max-width: 160px"
    },
    {
      field: "state",
      display: "State",
      sortable: true,
      style: "max-width: 160px"
    },
    {
      field: "zip",
      display: "Zip",
      sortable: true,
      style: "max-width: 120px"
    },
    {
      field: "primary_phone",
      display: "Primary Phone",
      sortable: true,
      style: "max-width: 160px"
    },
    {
      field: "primary_email",
      display: "Primary Email",
      sortable: true,
      style: "max-width: 250px"
    },
    {
      field: "secondary_phone",
      display: "Secondary Phone",
      sortable: true,
      style: "max-width: 160px"
    },
    {
      field: "secondary_email",
      display: "Secondary Email",
      sortable: true,
      style: "max-width: 250px"
    }
  ]
}
