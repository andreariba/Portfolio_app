import dash_bootstrap_components as dbc

def Navbar():

  navbar = dbc.NavbarSimple(
    children = [
      dbc.NavItem(dbc.NavLink("Allocation", href="allocation")),
      dbc.NavItem(dbc.NavLink("Forecast", href="forecast")),
      dbc.NavItem(dbc.NavLink("Home", href="home")),
			
#      dbc.DropdownMenu(
#        nav=True,
#	in_navbar=True,
#	label="Menu",
#        children=[
#          dbc.DropdownMenuItem("Entry 1"),
#          dbc.DropdownMenuItem("Entry 2"),
#          dbc.DropdownMenuItem(divider=True), 
#          dbc.DropdownMenuItem("Entry 3"),
#        ],
#      ),
    ],
    brand="Portfolio App",
    brand_href="home",
    sticky="top"
  )
    
  return navbar
