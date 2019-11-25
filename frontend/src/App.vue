<template>
  <div id="app">
    <div id="nav">
      <header class="navbar" role="banner">

    <div class="container">

      <div class="navbar-header">
        <button class="navbar-toggle" type="button" data-toggle="collapse"
        data-target=".navbar-collapse">
          <span class="sr-only">Toggle navigation</span>
          <i class="fa fa-cog"></i>
        </button>

        <a class="navbar-brand navbar-brand-img">
          <img id="logo" alt="GIS Support logo" src="@/assets/logo.png">
        </a>
      </div> <!-- /.navbar-header -->
      <nav class="collapse navbar-collapse" role="navigation">

        <ul class="nav navbar-nav navbar-right">

          <li class="dropdown navbar-profile">
            <a class="dropdown-toggle" style="padding-left: 15px;" data-toggle="dropdown"
            href="javascript:;" >
              <span>username &nbsp;</span>
              <i class="fa fa-caret-down"></i>
            </a>

            <ul class="dropdown-menu" role="menu">
              <li>
                <a>
                  <i class="fa fa-sign-out"></i>
                  &nbsp;&nbsp;<span>Wyloguj się</span>
                </a>
              </li>

            </ul>

          </li>
        </ul>
      </nav>
    </div> <!-- /.container -->

  </header>


    </div>
    <router-view/>
  </div>
</template>

<style>
  #logo {
    height: 50px;
  }
</style>
