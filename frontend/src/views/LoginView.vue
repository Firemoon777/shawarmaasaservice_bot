<template>
  <div class="text-center">
    <div class="spinner-border" role="status" v-if="access_granted">
      <span class="visually-hidden">Loading...</span>
    </div>
    <div class="card text-center" v-if="!access_granted">
      <img src="/access.png" class="card-img-top" alt="...">
      <div class="card-body">
        <h5>Для доступа необходимо выполнить вход в приложение.</h5>
        Бот получит доступ к вашему нику, имени и фотографии профиля. Это необходимо для идентификации человека, который выполняет заказ. В WebApp версии было также.
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LoginView",
  computed: {
    event_id: function () {
      return this.$route.query.event_id
    },
    user_id: function () {
      return this.$route.query.id
    },
    first_name: function () {
      return this.$route.query.first_name
    },
    last_name: function () {
      return this.$route.query.last_name
    },
    photo_url: function () {
      return this.$route.query.photo_url
    },
    auth_date: function () {
      return this.$route.query.auth_date
    },
    username: function () {
      return this.$route.query.username
    },
    hash: function () {
      return this.$route.query.hash
    },
    access_granted: function () {
      return !!this.hash
    }
  },
  methods: {

  },
  created() {
    if(!this.access_granted) return;
    let data = {
      event_id: this.event_id,
      id: this.user_id,
      first_name: this.first_name,
      last_name: this.last_name,
      photo_url: this.photo_url,
      auth_date: this.auth_date,
      username: this.username,
      hash: this.hash
    }
    let self = this
    axios.post("/login/", data).then(function (response) {
      console.log(response.data)
      localStorage.user_id = self.user_id
      localStorage.photo_url = self.photo_url
      localStorage.first_name = self.first_name
      localStorage.last_name = self.last_name
      if(self.event_id) {
        self.$router.push({
          path: "/market/" + self.event_id
        })
      } else {
        self.$router.push({
          path: "/"
        })
      }
    }).catch(function (error) {
      self.hash = ""
    })
  }
}
</script>

<style scoped>
.card {
        margin: 0 auto; /* Added */
        float: none; /* Added */
        margin-bottom: 10px; /* Added */
}
</style>