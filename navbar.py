import dash_bootstrap_components as dbc

def Navbar():

  navbar = dbc.NavbarSimple(
    children = [
      dbc.NavItem(dbc.NavLink("Overview", href="overview")),
      dbc.NavItem(dbc.NavLink("Allocation", href="allocation")),
      dbc.NavItem(dbc.NavLink("Forecast", href="forecast")),
      dbc.NavItem(dbc.NavLink("Home", href="home")),
    ],
    brand="Portfolio App",
    brand_href="home",
    sticky="top"
  )
    
  return navbar
