import { useHttp, usePublicHttp } from "../composables/useHttp.js"
import axios from "axios"

export default class UploadApi {
  BUCKET_NAME = "secure-photo-upload"

  constructor() {}

  /**
         * This will be used to get a presigned and secure url for users to upload photos to the s3 bucket
         * @param {string} fileName This will be just the string representation of the file that is being uploaded
         * @param {string} contentType This is the type for the file that is being uploaded
         * @returns {Dict} {
     "request": {
        "url": "string",
        "fields": {
        "key": "string",
        "content_type": "string",
        "acl": "string",
        "AWSAccessKeyId": "string",
        "policy": "string",
        "signature": "string"
        }
    },
    "id": "string"
    }
        */
  async getPresignedPostUrl(
    fileName,
    contentType,
    folderType,
    accountId,
    orderId = null,
    productId = null
  ) {
    let data = {
      file_name: fileName,
      content_type: contentType,
      folder_type: folderType,
      account_id: accountId,
      order_id: orderId,
      other_product_id: productId
    }
    let path = "/generate_presigned_post_url"
    let method = "POST"
    let respone = await usePublicHttp(path, method, data)
    return respone
  }

  /**
     * Once the file has been uploaded to s3, then this method will take the s3 filename of the object and insert it into the database
     * @param {string} fileName
     * @param {string} contentType
     * @param {int} accountId
     * @returns {Dict} {
     "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created_at": "2023-09-08T13:37:18.972Z",
    "modified_at": "2023-09-08T13:37:18.972Z",
    "filename": "string",
    "content_type": "string",
    "account_id": 2147483647
    }
    */
  async dbUploadFile(
    fileName,
    contentType,
    accountId,
    folderType,
    orderId = null,
    productId = null
  ) {
    let data = {
      filename: fileName,
      content_type: contentType,
      account_id: accountId,
      folder_type: folderType,
      order_id: orderId,
      other_product_id: productId
    }
    let path = "/db_upload_file"
    let method = "POST"
    return await usePublicHttp(path, method, data)
  }

  async dbUpdateFile(
    fileName,
    contentType,
    accountId,
    folderType,
    orderId = null,
    productId = null,
    id
  ) {
    let data = {
      filename: fileName,
      content_type: contentType,
      account_id: accountId,
      folder_type: folderType,
      order_id: orderId,
      other_product_id: productId
    }
    let path = `/db_upload_file/${id}`
    let method = "PATCH"
    return await usePublicHttp(path, method, data)
  }

  async deleteExistingFile(id, accountId) {
    let path = `/db_delete_file/${id}/${accountId}`
    let method = "DELETE"
    return await usePublicHttp(path, method)
  }

  async getPresignedGetUrl(
    fileName,
    folderType,
    accountId,
    orderId = null,
    productId = null
  ) {
    let data = {
      bucket_name: this.BUCKET_NAME,
      object_name: fileName,
      folder_type: folderType,
      account_id: accountId,
      order_id: orderId,
      other_product_id: productId
    }
    let path = "/generate_presigned_get_url"
    let method = "POST"
    let respone = await useHttp(path, method, data)

    return respone
  }

  async sendUpdateToS3(
    fileName,
    fileBytes,
    contentType,
    folderType,
    accountId,
    orderId = null,
    productId = null,
    fileUpdloadId,
    callback = () => {}
  ) {
    const file = fileBytes
    const formData = new FormData()

    const response = await this.getPresignedPostUrl(
      fileName,
      contentType,
      folderType,
      parseInt(accountId),
      orderId,
      productId
    )
    const data = response.data.value // Access the data property from the response
    formData.append("key", data.request.fields.key)
    formData.append("AWSAccessKeyId", data.request.fields.AWSAccessKeyId)
    formData.append("acl", data.request.fields.acl)
    formData.append("Content-Type", data.request.fields.content_type)
    formData.append("policy", data.request.fields.policy)
    formData.append("Signature", data.request.fields.signature)
    formData.append("file", file)

    let headers = {
      "Content-Type": "multipart/form-data"
    }
    try {
      let s3Response = await axios.post(data.request.url, formData, {
        headers: headers
      })
    } catch (e) {
      console.error(e)
      throw e
    }

    callback()

    try {
      let dbResponse = await this.dbUpdateFile(
        fileName,
        contentType,
        parseInt(accountId),
        folderType,
        orderId,
        productId,
        fileUpdloadId
      )
    } catch (e) {
      console.error(e)
    }
  }
  async sendToS3(
    fileName,
    fileBytes,
    contentType,
    folderType,
    accountId,
    orderId = null,
    productId = null,
    callback = () => {}
  ) {
    const file = fileBytes
    const formData = new FormData()

    const response = await this.getPresignedPostUrl(
      fileName,
      contentType,
      folderType,
      parseInt(accountId),
      orderId,
      productId
    )
    const data = response.data.value // Access the data property from the response
    formData.append("key", data.request.fields.key)
    formData.append("AWSAccessKeyId", data.request.fields.AWSAccessKeyId)
    formData.append("acl", data.request.fields.acl)
    formData.append("Content-Type", data.request.fields.content_type)
    formData.append("policy", data.request.fields.policy)
    formData.append("Signature", data.request.fields.signature)
    formData.append("file", file)

    let headers = {
      "Content-Type": "multipart/form-data"
    }
    try {
      let s3Response = await axios.post(data.request.url, formData, {
        headers: headers
      })
    } catch (e) {
      console.error(e)
      throw e
    }

    callback()

    try {
      let dbResponse = await this.dbUploadFile(
        fileName,
        contentType,
        parseInt(accountId),
        folderType,
        orderId,
        productId
      )
    } catch (e) {
      console.error(e)
    }
  }
}
