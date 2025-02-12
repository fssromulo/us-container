import formatCurrency from "../utils/formatCurrency"
import QuoteGenerationService from "@/service/QuoteGeneration"
import { useCustomerOrder } from "@/store/modules/customerOrder"
import cloneDeep from "lodash.clonedeep"
import { useTaxes } from "../store/modules/taxes"
import { roundHalfUp } from "@/utils/formatCurrency.js"

export default class Cart {
  quoteService = new QuoteGenerationService()
  customerOrderStore = useCustomerOrder()
  taxesStore = useTaxes()

  roundIt = (number, decimalPlaces = null) => {
    let returnNum = 0
    decimalPlaces == null
      ? (returnNum = Math.round(number))
      : (returnNum = Math.round(number * 10 ** decimalPlaces) / 100)
    return returnNum
  }

  getCartTotal = (cart, downpayment_strategy) => {
    let total = 0
    total = cart.reduce((total, product) => {
      return (
        total +
        roundHalfUp(this.addTotalForItem(product, 0, downpayment_strategy))
      )
    }, 0)
    return total
  }
  getTotalCartRTO = (cart) => {
    return cart.reduce((total, product) => {
      if (product.total_rental_price !== undefined) {
        return total + roundHalfUp(product.total_rental_price)
      } else {
        return total + 0
      }
    }, 0)
  }

  getCartShippingTotal = (cart) => {
    return cart.reduce((total, product) => {
      return total + product.shipping_revenue
    }, 0)
  }

  getTotalTax = (cart) => {
    return cart.reduce((total, product) => {
      let tax = 0
      if (product.tax != 0) {
        tax = total + roundHalfUp(product.tax)
      }
      return tax
    }, 0)
  }

  getCartSubTotal = (cart) => {
    return cart.reduce((total, product) => {
      return total + product.subTotal
    }, 0)
  }

  getBankFeeTotal = (cart) => {
    return cart.reduce((total, product) => {
      return total + product.convenience_fee
    }, 0)
  }

  getCartQuantity = (cart) => {
    return cart.reduce((total, product) => {
      return total + product.quantity
    }, 0)
  }

  isPickupAddress = (cart) => {
    return cart.every((c) => c.shipping_revenue === 0)
  }

  formatCart = (cart) => {
    return cart.map((c) => {
      return Object.assign({}, c, {
        revenue: formatCurrency(c.revenue),
        subTotal: formatCurrency(c.subTotal),
        convenience_fee: formatCurrency(c.convenience_fee),
        tax: formatCurrency(Number(c.tax)),
        shipping_revenue: formatCurrency(c.shipping_revenue),
        container_plus_shipping: formatCurrency(c.container_plus_shipping),
        interest_owed: formatCurrency(c.interest_owed),
        total_rental_price: formatCurrency(c.total_rental_price),
        display_monthly_owed: formatCurrency(c.monthly_owed),
        thirtyDayPrice: formatCurrency(c.thirtyDayPrice)
      })
    })
  }

  doesItemExist = (item) => {
    return item !== undefined && item !== null && !Number.isNaN(item)
  }

  reducedCart = (cart) => {
    let reducedCart = cart.reduce((acc, item) => {
      const found = acc.find((i) => i.title === item.title)
      if (found) {
        found.quantity += item.quantity
        found.revenue +=
          typeof item.revenue !== "undefined" ? item.revenue : item.price
        found.shipping_revenue += this.roundIt(item.shipping_revenue || 0, 2)
        // found.tax += Number(item.tax);
        found.convenience_fee += item.convenience_fee
        found.subTotal += item.subTotal
        found.container_plus_shipping += item.container_plus_shipping
        found.interest_owed += item.interest_owed
        found.total_rental_price += this.roundIt(
          item.total_rental_price || 0,
          2
        )
        if (this.doesItemExist(item.monthly_owed)) {
          found.monthly_owed += this.roundIt(item.monthly_owed || 0, 2)
        }
        if (this.doesItemExist(item.monthly_price)) {
          found.monthly_price += this.roundIt(item.monthly_price, 2)
        }
        found.thirtyDayPrice += item.thirtyDayPrice
        return acc
      } else {
        if (this.doesItemExist(item.monthly_owed)) {
          item.monthly_owed = this.roundIt(item.monthly_owed || 0, 2)
        }
        if (this.doesItemExist(item.monthly_price)) {
          item.monthly_price = this.roundIt(item.monthly_price, 2)
        }
        return acc.concat(item)
      }
    }, [])
    return reducedCart
  }

  calculateConvenienceFee = (c, rate) => {
    return (
      (Number(c.shipping_revenue) + Number(c.revenue) + Number(c.tax)) *
      Number(rate)
    )
  }

  dtoOrderToCart = (
    order,
    calcConvFee,
    rate,
    downpayment_strategy = null,
    country = null
  ) => {
    const mappedCart = order.line_items
      .filter((a) => !a.product_type || a.product_type === "CONTAINER")
      .map((c) => {
        let bankFee = 0
        if (calcConvFee) {
          this.calculateConvenienceFee(c, rate)
        } else {
          c.convenience_fee
        }
        // if (order.calculated_remaining_balance < order.calculated_total_price && !calcConvFee.convenience_fee) {
        //   const reCalculatedBankFee = this.calculateConvenienceFee(c, rate)
        //   const amountPaid = order.calculated_total_price - order.calculated_remaining_balance
        //   const feeReduction = (amountPaid / order.line_items.length) * rate
        //   bankFee = reCalculatedBankFee - feeReduction
        // }

        const product_location = `${c.product_city}, ${c.product_state}`
        let product_prefix = c.container_size || c.accessory_id
        const id =
          product_prefix +
          c.condition +
          c.rent_period +
          JSON.stringify(c.attributes)

        let shipping_revenue
        if (
          downpayment_strategy == null ||
          downpayment_strategy == undefined ||
          downpayment_strategy == ""
        ) {
          shipping_revenue = this.roundIt(c.shipping_revenue, 2)
        } else if (
          downpayment_strategy == "FIRST_MONTH_PLUS_DELIVERY_&_PICKUP"
        ) {
          shipping_revenue = this.roundIt(2 * c.shipping_revenue, 2)
        } else if (downpayment_strategy == "FIRST_MONTH_PLUS_DELIVERY") {
          shipping_revenue = this.roundIt(c.shipping_revenue, 2)
        } else {
          shipping_revenue = 0
        }
        let applied_discount = 0
        c.coupon_line_item_values.forEach((coupon) => {
          applied_discount = applied_discount + coupon.amount
        })

        const container_plus_shipping = c.revenue + shipping_revenue
        return {
          id: id,
          product_id: c.id,
          title: c.title,
          abrev_title: c.abrev_title,
          abbrev_title_w_container_number: c.abbrev_title_w_container_number,
          has_accessories: c.has_accessories,
          has_containers: c.has_containers,
          calculated_rental_name: c.calculated_rental_name,
          revenue: c.revenue + applied_discount,
          applied_discount: applied_discount,
          shipping_revenue: shipping_revenue,
          tax: Number(c.tax),
          quantity: 1,
          convenience_fee: bankFee,
          door_orientation: "Facing Cab",
          container_size: c.container_size,
          condition: c.condition,
          subTotal: this.addTotalForItem(c, bankFee),
          thirtyDayPrice: this.getThirtyDayPrice(c),
          product_location: product_location,
          delivery_location: `${order.address.city}, ${order.address.state}`,
          container_plus_shipping: container_plus_shipping,
          rent_period: c.rent_period,
          interest_owed: c.interest_owed,
          total_rental_price: c.total_rental_price,
          monthly_owed: c.monthly_owed,
          type: order.type,
          container_number:
            c.inventory == null ? "None" : c.inventory.container_number,
          attributes: c.attributes
        }
      })

    return this.reducedCart(mappedCart)
  }

  dtoOrderAccessoryToCart = (order, calcConvFee, rate) => {
    const mappedCart = order.line_items
      .filter((a) => a.product_type && a.product_type !== "CONTAINER")
      .map((c) => {
        let bankFee = 0
        if (calcConvFee) {
          this.calculateConvenienceFee(c, rate)
        } else {
          c.convenience_fee
        }

        const file_upload =
          c.accessory_line_item.length > 0
            ? {
                filename: c.accessory_line_item[0].filename,
                content_type: c.accessory_line_item[0].content_type,
                folder_type: c.accessory_line_item[0].folder_type,
                account_id: c.accessory_line_item[0].other_product.account_id,
                order_id: order.id,
                other_product_id: c.accessory_line_item[0].other_product.id
              }
            : {}

        const id = c.other_product_name
        const container_plus_shipping =
          c.revenue + this.roundIt(c.shipping_revenue || 0, 2)
        let applied_discount = 0

        c.coupon_line_item_values.forEach((coupon) => {
          applied_discount = applied_discount + coupon.amount
        })
        return {
          id: id,
          title: c.title,
          revenue: c.revenue + applied_discount,
          applied_discount: applied_discount,
          shipping_revenue: this.roundIt(c.shipping_revenue || 0, 2),
          tax: Number(c.tax),
          shipping: c.other_product_shipping_time,
          quantity: 1,
          convenience_fee: bankFee,
          container_size: c.container_size,
          condition: c.condition,
          subTotal: this.addTotalForItem(c, bankFee),
          thirtyDayPrice: this.getThirtyDayPrice(c),
          delivery_location: `${order.address.city}, ${order.address.state}`,
          container_plus_shipping: container_plus_shipping,
          rent_period: c.rent_period,
          interest_owed: c.interest_owed,
          total_rental_price: c.total_rental_price,
          monthly_owed: c.monthly_owed,
          type: order.type,
          attributes: c.attributes,
          product_location: `${c.product_city}, ${c.product_state}`,
          product_link:
            c.accessory_line_item[0]?.other_product?.product_link || "",
          file_upload: file_upload
        }
      })

    return this.reducedCart(mappedCart)
  }

  generateId = (c) => {
    return c.container_size
      ? c.id + c.price + c.title.replaceAll(" ", "")
      : c.accessory_id +
          c.condition +
          this.addTotalForItem(c).toString() +
          c?.rent_period
  }

  dtoProductToCart = (cart, payment_strategy = "") => {
    const mappedCart = cart.map((c) => {
      const product_location = `${c.city}, ${c.state}`
      const revenue =
        c.revenue !== undefined
          ? c.revenue
          : c.sale_price !== undefined
          ? c.sale_price
          : c.price
      const id = this.generateId(c)
      const container_plus_shipping =
        revenue + this.roundIt(c.shipping_revenue || 0, 2)

      let shipping_revenue = this.roundIt(c.shipping_revenue || 0, 2)

      const addr = this.customerOrderStore.address
      if (addr.province != null && addr.province != "") {
        addr.state = addr.province
      }
      if (c.product_type === "PORTABLE_CONTAINER") {
        c.attributes["portable"] = true
      }
      return {
        id: id,
        title: c.title,
        revenue: revenue,
        price: c.price,
        product_type: c.product_type,
        product_id: c.id,
        shipping: c.shipping || "",
        shipping_revenue: shipping_revenue,
        tax: Number(c.tax || 0),
        quantity: 1,
        potential_miles: c.distance,
        convenience_fee: c.convenience_fee || 0,
        door_orientation: "Facing Cab",
        container_size: c.container_size,
        condition: c.condition,
        subTotal: this.addTotalForItem(c),
        thirtyDayPrice: this.getThirtyDayPrice(c),
        product_location: product_location,
        delivery_location: `${addr.city}, ${addr.state}`,
        container_plus_shipping: container_plus_shipping,
        rent_period: c.rent_to_own?.rent_period,
        total_rental_price: c.rent_to_own?.total_rental_price,
        monthly_owed: c.rent_to_own?.monthly_owed || c.monthly_owed,
        type: c.type,
        attributes: c.attributes,
        product_city: c.city,
        product_state: c.state,
        file_upload_id:
          c.file_upload && c.file_upload.length > 0
            ? c.file_upload[0].id
            : null,
        destination_state: c.destination_state
      }
    })
    return mappedCart
  }

  displayCart = (cart) => {
    let returnDisplayCart = this.formatCart(cloneDeep(this.reducedCart(cart)))
    return returnDisplayCart
  }

  dtoCartToAccessoryOrder = (cart) => {
    const addr = this.customerOrderStore.address
    const mappedCart = cart
      .filter((item) => item.product_type === "CONTAINER_ACCESSORY")
      .map((c) => {
        const res = {
          minimum_shipping_cost: c.minimum_shipping_cost,
          product_id: c.product_id || "",
          product_type: c.product_type,
          potential_dollar_per_mile: c.cost_per_mile,
          potential_miles: c.potential_miles,
          revenue: c.revenue,
          door_orientation: "",
          shipping_revenue: this.roundIt(c.shipping_revenue || 0, 2),
          tax: Number(c.tax || 0),
          convenience_fee: c.convenience_fee,
          product_city: c.product_city,
          product_state: c.product_state,
          container_size: c.container_size,
          condition: c.condition,
          rent_period: c.rent_period,
          total_rental_price: c.total_rental_price,
          monthly_owed: c.monthly_owed,
          attributes: c.attributes || "",
          file_upload_id: c.file_upload_id,
          destination_state: c.destination_state
        }
        return res
      })

    const customerOrder = {
      first_name: "",
      last_name: "",
      email: "",
      company_name: "",
      phone: "",
      order: {
        line_items: mappedCart,
        address: {
          street_address: addr.street_address || "",
          city: addr.city,
          state: addr.state,
          zip: addr.zip,
          county: addr.county
        },
        type: cart[0].type,
        remaining_balance: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        sub_total_price: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        total_price: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        tax: this.getTotalTax(mappedCart)
      }
    }
    return customerOrder
  }

  dtoCartToContainerOrder = (cart, pairs = []) => {
    const addr = this.customerOrderStore.address
    const mappedCart = cart
      .filter((item) => item.product_type !== "CONTAINER_ACCESSORY")
      .map((c) => {
        const res = {
          minimum_shipping_cost: c.minimum_shipping_cost,
          product_id: c.product_id || "",
          product_type: c.product_type || "SHIPPING_CONTAINER",
          potential_dollar_per_mile: c.cost_per_mile,
          potential_miles: c.potential_miles,
          revenue: c.revenue,
          shipping_revenue: this.roundIt(c.shipping_revenue || 0, 2),
          tax: Number(c.tax || 0),
          convenience_fee: c.convenience_fee,
          door_orientation: "Facing Cab",
          product_city: c.product_city,
          product_state: c.product_state,
          container_size: c.container_size,
          condition: c.condition,
          rent_period: c.rent_period,
          total_rental_price: c.total_rental_price,
          monthly_owed: c.monthly_owed,
          attributes: c.attributes || "",
          destination_state: c.destination_state
        }

        const attributes = {}

        pairs.forEach((pair) => {
          if (c.title.includes(pair.name)) {
            attributes[pair.value] = true
          }
        })

        res.attributes = attributes
        if (c.container_size == "40" && c.type == "RENT") {
          res.attributes = { high_cube: true }
        }

        return res
      })

    const customerOrder = {
      first_name: "",
      last_name: "",
      email: "",
      company_name: "",
      phone: "",
      order: {
        line_items: mappedCart,
        address: {
          street_address: addr.street_address || "",
          city: addr.city,
          state: addr.state,
          zip: addr.zip,
          county: addr.county
        },
        type: cart[0].type,
        remaining_balance: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        sub_total_price: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        total_price: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        tax: this.getTotalTax(mappedCart)
      }
    }
    return customerOrder
  }

  dtoCartToOrder = (cart) => {
    const addr = this.customerOrderStore.address
    const mappedCart = cart.map((c) => {
      const res = {
        minimum_shipping_cost: c.minimum_shipping_cost,
        product_id: c.product_id || "",
        product_type: c.product_type || "SHIPPING_CONTAINER",
        potential_dollar_per_mile: c.cost_per_mile,
        potential_miles: c.potential_miles,
        revenue: c.revenue,
        shipping_revenue: this.roundIt(c.shipping_revenue || 0, 2),
        tax: Number(c.tax || 0),
        convenience_fee: c.convenience_fee,
        door_orientation: "Facing Cab",
        product_city: c.product_city,
        product_state: c.product_state,
        container_size: c.container_size,
        condition: c.condition,
        rent_period: c.rent_period,
        total_rental_price: c.total_rental_price,
        monthly_owed: c.monthly_owed,
        attributes: c.attributes || ""
      }

      const attributes = {}
      if (c.title.includes("High Cube")) {
        attributes["high_cube"] = true
      }

      if (c.title.includes("Double Door")) {
        attributes["double_door"] = true
      }

      if (c.title.includes("Standard")) {
        attributes["standard"] = true
      }
      res.attributes = attributes

      if (c.container_size == "40" && c.type == "RENT") {
        res.attributes = { high_cube: true }
      }

      return res
    })

    const customerOrder = {
      first_name: "",
      last_name: "",
      email: "",
      company_name: "",
      phone: "",
      order: {
        line_items: mappedCart,
        address: {
          street_address: addr.street_address || "",
          city: addr.city,
          state: addr.state,
          zip: addr.zip,
          county: addr.county
        },
        type: cart[0].type,
        remaining_balance: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        sub_total_price: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        total_price: mappedCart
          .map((c) => this.roundIt(this.addTotalForItem(c), 2))
          .reduce((a, b) => a + b, 0),
        tax: this.getTotalTax(mappedCart)
      }
    }
    return customerOrder
  }

  recalculateTax = (cartItem, taxes) => {
    let taxRate
    if (cartItem.product_state !== undefined) {
      taxRate = taxes.find((s) => s.state === cartItem.product_state)?.rate || 0
    } else {
      // The variables are named different when we are going from generate quote to cart and from order to cart
      taxRate = taxes.find((s) => s.state === cartItem.state)?.rate || 0
    }

    if (cartItem.revenue !== undefined) {
      return this.roundIt(
        (cartItem.revenue + cartItem.shipping_revenue) * taxRate,
        2
      )
    } else {
      return this.roundIt(
        (cartItem.price + cartItem.shipping_revenue) * taxRate,
        2
      )
    }
  }

  addTotalForItem = (
    item,
    convenience_fee = 0,
    down_payment_strategy = undefined
  ) => {
    if (item.type === "RENT") {
      const shipping = Number(item?.shipping_revenue)
      if (down_payment_strategy == "FIRST_MONTH_PLUS_DELIVERY_&_PICKUP") {
        return (
          this.roundIt(item.monthly_owed, 2) + this.roundIt(2 * shipping, 2)
        )
      } else if (down_payment_strategy == "FIRST_MONTH_PLUS_DELIVERY") {
        return this.roundIt(item.monthly_owed, 2) + this.roundIt(shipping, 2)
      } else {
        return this.roundIt(item.monthly_owed, 2)
      }
    }

    // If monthly_owed is undefined, calculate return_amount
    const revenue =
      item.revenue !== undefined && item.revenue !== null
        ? item.revenue
        : item.sale_price !== undefined && item.sale_price !== null
        ? item.sale_price
        : item.price
    const shippingRevenue = Number(item?.shipping_revenue || 0)
    const totalAmount = this.roundIt(Number(revenue) + shippingRevenue, 2)
    return totalAmount
  }

  getThirtyDayPrice = (item) => {
    let price
    let taxAmt = 0
    if (item.tax != 0) {
      let taxes = this.taxesStore.taxes
      taxAmt = this.recalculateTax(item, taxes)
    }
    if (item.revenue !== undefined) {
      price = this.roundIt(
        Number(item.revenue) + Number(item?.shipping_revenue) + Number(taxAmt),
        2
      )
    } else {
      price = this.roundIt(
        Number(item.price) + Number(item?.shipping_revenue) + Number(taxAmt),
        2
      )
    }
    return price
  }

  abrevTitle = (item) => {
    let highCube = !item.attributes
      ? "STD"
      : item.attributes.high_cube
      ? "HC"
      : "STD"
    let doubleDoor = !item.attributes
      ? ""
      : item.attributes.double_door
      ? "Double Door"
      : ""
    let type = `${doubleDoor} ${highCube}`.trim()
    let productType = !item.attributes
      ? ""
      : !item.attributes.portable
      ? ""
      : "Portable"

    return `${item.container_size}' ${item.condition} ${type} ${productType}`.trim()
  }

  rentalTitle = (item) => {
    let highCube = !item.attributes
      ? "Standard"
      : item.attributes.high_cube
      ? "High Cube"
      : "Standard"
    let type = `${highCube}`.trim()
    return `${item.container_size}' ${type}`.trim()
  }

  containerImages = [
    {
      attributes: "ALL",
      container_size: 20,
      image: "/images/blocks/20_standard_container.png"
    },
    {
      attributes: "high_cube",
      container_size: 40,
      image: "/images/blocks/40_high_cube_container.png"
    },
    {
      attributes: "standard",
      container_size: 40,
      image: "/images/blocks/40_standard_container.png"
    }
  ]

  cartColumnsRTO = [
    {
      label: "Shipping Container",
      field: "title"
    },
    {
      label: "Shipping Container",
      field: "abrev_title"
    },
    {
      label: "Delivery From",
      field: "product_location"
    },
    {
      label: "Delivery To",
      field: "delivery_location"
    },
    {
      label: "Quantity",
      field: "quantity"
    },
    {
      label: "RTO Period",
      field: "rent_period"
    },
    {
      label: "Sales Tax",
      field: "tax"
    }
  ]

  cartColumnsRental = [
    {
      label: "Shipping Container",
      field: "title"
    },
    {
      label: "Shipping Container",
      field: "abrev_title"
    },
    {
      label: "Delivery From",
      field: "product_location"
    },
    {
      label: "Delivery To",
      field: "delivery_location"
    },
    {
      label: "Quantity",
      field: "quantity"
    },
    {
      label: "Monthly Rent",
      field: "display_monthly_owed"
    },
    {
      label: "Sales Tax",
      field: "tax"
    }
  ]

  cartColumnsPurchase = [
    {
      label: "Shipping Container",
      field: "title"
    },
    {
      label: "Shipping Container",
      field: "abrev_title"
    },
    {
      label: "Delivery From",
      field: "product_location"
    },
    {
      label: "Delivery To",
      field: "delivery_location"
    },
    {
      label: "Quantity",
      field: "quantity"
    },
    {
      label: "Container Price",
      field: "revenue"
    },
    {
      label: "Container & Shipping",
      field: "subTotal"
    },
    {
      label: "Shipping",
      field: "shipping_revenue"
    },
    {
      label: "Total",
      field: "subTotal"
    }
  ]

  cartColumnsAccessory = [
    {
      label: "Delivery From",
      field: "product_location"
    },
    {
      label: "Delivery To",
      field: "delivery_location"
    },
    {
      label: "Quantity",
      field: "quantity"
    },
    {
      label: "Shipping",
      field: "shipping_revenue"
    },
    {
      label: "Total",
      field: "subTotal"
    }
  ]

  cartColumnsPickup = [
    {
      label: "Shipping Container",
      field: "title"
    },
    {
      label: "Shipping Container",
      field: "abrev_title"
    },
    {
      label: "Pickup From",
      field: "product_location"
    },
    {
      label: "Quantity",
      field: "quantity"
    },
    {
      label: "Container Price",
      field: "revenue"
    },
    {
      label: "Sales Tax",
      field: "tax"
    },
    {
      label: "Total",
      field: "subTotal"
    }
  ]

  cartColumnsAccessories = [
    {
      label: "Accessory",
      field: "title"
    },
    {
      label: "",
      field: "image_link"
    },
    {
      label: "",
      field: "product_link"
    },
    {
      label: "Price",
      field: "price"
    },
    {
      label: "Quantity",
      field: "quantity"
    },
    {
      label: "Accessory Shipping",
      field: "shipping"
    },
    {
      label: "Total",
      field: "subTotal"
    }
  ]

  cartOrderColumnsAccessories = [
    {
      label: "Accessory",
      field: "title"
    },
    {
      label: "",
      field: "image_link"
    },
    {
      label: "",
      field: "product_link"
    },
    {
      label: "Price",
      field: "revenue"
    },
    {
      label: "Quantity",
      field: "quantity"
    },
    {
      label: "Accessory Shipping",
      field: "shipping"
    },
    {
      label: "Total",
      field: "subTotal"
    }
  ]
}
