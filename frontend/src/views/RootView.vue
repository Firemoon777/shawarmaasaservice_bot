<template>
  <div>
    Текущие события:
    <button type="button" class="btn btn-primary" v-for="event in this.events" v-on:click="this.$router.push({path: '/event/' + event.id})">Событие {{event.id}}</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RootView",
  data() {
    return {
      events: []
    }
  },
  created() {
    let self = this
    axios.get("/profile/own_events").then(function (response) {
      self.events = response.data
    })
  }
}
</script>

<style scoped>

</style>