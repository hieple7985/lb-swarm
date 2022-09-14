import {React} from 'react';
import './header.css';

const Header = () => {

    return (
        <>
        <nav className="navbar navbar-inverse">
                <div className="container-fluid">
                    <div className="navbar-header">
                        <a className="navbar-brand" href="/">LaSwarm</a>
                    </div>
                    <ul className="nav navbar-nav">
                        <li><a href="/" >Search</a></li>
                        <li><a onClick={function(){fetch("http://localhost:8000/extract")}}>Extract</a></li>
                    </ul>
                    <button className="btn btn-danger navbar-btn" id="about">About</button>
                </div>
            </nav>
        </>
    )
}

export default Header;