import React from 'react';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import FormPage from "./components/form";
import ResultPage from "./components/result";
import './App.css';


function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={FormPage} />
        <Route exact path="/result" component={ResultPage} />
      </Switch>
    </Router>
  );
}

export default App;
