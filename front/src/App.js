import React from 'react';
import './App.css';
import Header from './components/header';
import  Search  from './Search';
import  { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
    return (
        <>
            <Header /> 
            <Search />
        </>
    );
}

export default App;