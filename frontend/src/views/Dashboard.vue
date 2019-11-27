<template>
  <div class="dashboard container align-center">
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-database"></i>
          <span data-i18n="dashboard.title"> {{$i18n.t('dashboard.title.vectorLayersList')}}</span>
        </div>
        <div class="p-0">
          <input type="text" class="form-control container__input" v-model="searchVector"
            :placeholder="$i18n.t('dashboard.placeholder.layersFilter')">
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main">
        <span data-toggle="modal" data-target="#addLayerModal" data-type="vectorLayer">
          <i class="fa fa-plus-circle fa-lg green pt-10" style="margin-right:5px;"></i>
          <a class="green">{{$i18n.t('dashboard.list.addLayer')}}</a>
        </span>
        <div v-if="filteredListVector.length == 0" class="pt-10 pb-10">
          {{$i18n.t('default.noLayers')}}
        </div>
        <template v-else v-for="(val, key) in filteredListVector">
          <div class="mb-0" :key="key">
            <div class="panel-heading pl-0 pr-0">
              <h4 class="panel-title flex-center">
                <span class="panel-title__names">
                  <i class="icon-li fa fa-map-o fa-lg mr-5"></i>
                  <span class="bold" href="#">
                    {{ val.name }}
                  </span>
                  <span class="desc-sm">
                    {{ val.team }}
                  </span>
                </span>
                <span class="panel-title__tools">
                  <i class="fa fa-cog fa-lg yellow icon-hover" data-toggle="tooltip"
                    data-placement="top" title="Ustawienia"></i>
                  <i class="fa fa-trash fa-lg red icon-hover" data-toggle="tooltip"
                    data-placement="top" title="Usuń"></i>
                </span>
              </h4>
            </div>
          </div>
        </template>
      </div>
    </div>

    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-database"></i>
          <span data-i18n="dashboard.title">
            {{$i18n.t('dashboard.title.externalSourcesList')}}
          </span>
        </div>
        <div class="p-0">
          <input type="text" class="form-control container__input" v-model="searchExtSources"
            :placeholder="$i18n.t('dashboard.placeholder.externalSourcesFilter')">
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main">
        <span data-toggle="modal" data-target="#addLayerModal" data-type="externalLayer">
          <i class="fa fa-plus-circle fa-lg green pt-10" style="margin-right:5px;"></i>
          <a class="green">{{$i18n.t('dashboard.list.addLayer')}}</a>
        </span>
        <div v-if="filteredListExternal.length == 0" class="pt-10 pb-10">
          {{$i18n.t('default.noLayers')}}
        </div>
        <template v-else v-for="(val, key) in filteredListExternal">
          <div class="mb-0" :key="key">
            <div class="panel-heading pl-0 pr-0">
              <h4 class="panel-title flex-center">
                <span class="panel-title__names">
                  <i class="icon-li fa fa-map-o fa-lg mr-5"></i>
                  <span class="bold" href="#">
                    {{ val.name }}
                  </span>
                  <span class="desc-sm">
                    {{ val.layType }}
                  </span>
                  <span class="desc-sm">
                    {{ val.url }}
                  </span>
                </span>
                <span class="panel-title__tools">
                  <i class="fa fa-cog fa-lg yellow icon-hover" data-toggle="tooltip"
                    data-placement="top" title="Ustawienia"></i>
                  <i class="fa fa-trash fa-lg red icon-hover" data-toggle="tooltip"
                    data-placement="top" title="Usuń"></i>
                </span>
              </h4>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!--MODAL DODAWANIA/EDYCJI PROJEKTÓW-->
    <div class="modal fade" data-backdrop="static" id="addLayerModal" tabindex="-1" role="dialog"
      aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{$i18n.t('dashboard.modal.addLayer')}}</h4>
          </div>
          <div class="modal-body">

          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">
              {{$i18n.t('default.cancel')}}
            </button>
            <button type="button" class="btn btn-success">{{$i18n.t('default.save')}}</button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->
  </div>
</template>

<script>

export default {
  name: 'dashboard',
  data: () => ({
    passwordModalVisible: false,
    searchExtSources: '',
    searchVector: '',
    vectorLayersList: [
      { name: 'brownfields', team: 'Hale' },
      { name: 'greenfields', team: 'Grunty inwestycyjne' },
    ],
    externalLayersList: [
      { name: 'Nadleśnictwa', layType: 'WMS', url: 'www.url.pl/wms' },
      { name: 'Podtopienia', layType: 'WMTS', url: 'www.url.pl/wmts' },
    ],
  }),
  computed: {
    filteredListExternal() {
      return this.externalLayersList.filter(
        layer => layer.name.toLowerCase().includes(this.searchExtSources.toLowerCase()),
      );
    },
    filteredListVector() {
      return this.vectorLayersList.filter(
        layer => layer.name.toLowerCase().includes(this.searchVector.toLowerCase()),
      );
    },
  },
  mounted() {
    this.$swagger.apis.Auth.post_api_login({ body: { user: 'test', password: 'test' } }).then((response) => {
      const { token } = response.obj;
      console.log(token);
    });
  },
};
</script>

<style scoped>
.container {
  top: 20px;
}
.container__input {
  width: 300px;
}
.dashboard.container {
  height: calc(100% - 76px);
  padding-left: 0px;
  padding-right: 0px;
}
.desc-sm {
  color: #b5b5b5;
  font-family: "Open Sans","Trebuchet MS",arial,sans-serif;
  font-size: 12px;
  letter-spacing: -1px;
  line-height: 1.75em;
  margin-left: 5px;
}
.heading-block:after {
  display: none;
}
.panel-title__names {
  font-size: 14px;
}
.panel-title__tools i:not(:last-child) {
  margin-right: 5px;
}
.section {
  height: 50%;
}
.section__header {
  padding-bottom: 15px;
  margin-bottom: -1px;
}
</style>
