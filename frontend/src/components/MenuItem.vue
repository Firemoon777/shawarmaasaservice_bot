<template>
    <div class="card">
        <div class="card-image">
            <figure class="image">
                <img src="https://bulma.io/images/placeholders/64x64.png" alt="Placeholder image">
            </figure>
        </div>
        <div class="card-content">
            <div class="content">
                <div class="item-title">
                   {{ item.name }}
                </div>
                <div class="item-price">
                    {{item.price}}₽
                </div>
            </div>
        </div>
        <footer class="card-footer">
            <a href="#" class="card-footer-item" v-if="!this.count" v-on:click="inc">Добавить</a>
            <a href="#" class="card-footer-item" v-if="this.count" v-on:click="dec">-</a>
            <a href="#" class="card-footer-item" v-if="this.count">{{this.count}}</a>
            <a href="#" class="card-footer-item" v-if="this.count" v-on:click="inc">+</a>
        </footer>
    </div>
</template>

<script>
    export default {
        name: "MenuItem",
        props: ["item"],
        data() {
          return {
              "count": 0
          }
        },
        methods: {
            inc() {
                this.count++
                this.$emit("count-changed", this.item.id, this.count)
            },
            dec() {
                this.count--
                if(this.count < 0) this.count = 0
                this.$emit("count-changed", this.item.id, this.count)
            }
        }
    }
</script>

<style scoped>
    .card {
        width: 110px;
        margin: 4px auto 21px;
        box-sizing: border-box;
        overflow-wrap: break-word;
        font-size: 13px;
        display: flex;
        flex-flow: column;
    }
    .card-image {
        flex: 0 1 auto;
    }
    .card-content {
        padding: 1rem 0.5rem;
        flex: 1 1 auto;
    }
    .card-footer {
        flex: 0 1 44px;
    }
    .item-price {
        padding-top: 10px;
    }
</style>