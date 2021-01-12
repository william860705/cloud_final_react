import React, { useState } from 'react';
import './App.css';
import Upload from './components/Upload'
import History from './components/History'

import {
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink,
  UncontrolledDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  NavbarText
} from 'reactstrap';
import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom'

function App(props) {
  const [isOpen, setIsOpen] = useState(false);

  const toggle = () => setIsOpen(!isOpen);

  return (
    <div>
      <Router>
    <div className='main'>
    <div>
      
      <Navbar color="light" light expand="md">
        <NavbarBrand tag={Link} to='/'>Main</NavbarBrand>
        <NavbarBrand tag={Link} to='/history'>History</NavbarBrand>
      </Navbar>
    </div>
  </div>
    <div className="App">
      <header className="App-header">

        {/* <p>
          Upload An Image For Processing
        </p> */}
        {/* <Upload /> */}
        <Route exact path="/" render={() => (
            <Upload />
          )}/>
        <Route exact path="/history" render={() => (
            <History />
          )}/>
      </header>
    </div>
    </Router>
    </div>
  );
}

export default App;
