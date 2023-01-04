<template>
  <div class="col-12">

    <div class="card">
      <div class="card-body">
        <button type="button" class="btn btn-primary" :disabled="loading" v-on:click="prolong(10)">Продлить событие на 10 минут</button>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        Доступны:
        <div class="form-check" v-for="item in menu">
          <input class="form-check-input" type="checkbox" value="" :id="'item'+item.id" v-model="item.leftover" :checked="item.leftover !== 0">
          <label class="form-check-label" :for="'item'+item.id">
            {{ item.name }}
          </label>
        </div>
        <button type="button" class="btn btn-primary" :disabled="loading" v-on:click="reorder(10)">Обновить остатки и запустить перезаказ</button>
      </div>
    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "EventView",
  props: ["id"],
  data() {
    return {
      event: {},
      menu: [],
      loading: false
    }
  },
  computed: {
    reorder_request_data: function() {
      let result = {}
      for(let i in this.menu) {
        result[this.menu[i].id] = !!this.menu[i].leftover
      }
      return result
    }
  },
  methods: {
    prolong(m) {
      let self = this
      this.loading = true
      axios.post("/control/" + this.id + "/prolong", {time: m}).then(function (response) {

      }).finally(function (response) {
        self.loading = false
      })
    },
    reorder: function (m) {
      let self = this
      this.loading = true
      let data = {
        time: m,
        entries: this.reorder_request_data
      }
      axios.post("/control/" + this.id + "/reorder", data).then(function (response) {

      }).finally(function (response) {
        self.loading = false
      })
    }
  },
  created() {
    let self = this
    axios.get("/control/" + this.id).then(function (response) {
      self.event = response.data.event
      self.menu = response.data.menu
      for(let item in self.menu) {
        response.data.menu[item].leftover = !!response.data.menu[item].leftover
      }
    })
  }
}
</script>

<style scoped>

</style>