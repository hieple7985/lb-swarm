import React from 'react';
import { useState,useEffect } from 'react';
import './Search.css';

const Search = () => {
    const [files, setFiles] = useState([]);
    const [searching, setSearching] = useState('');
    const [isSearch, setIsSearch] = useState(false);
    const [buttonSearch, setButtonSearch] = useState(true);
    const [isIframe, setIsIframe] = useState(true);   
    
 
    const searched = (e) => {
        e.preventDefault();
        setSearching(e.target.value);
    }
    const getData = () => {

        const res = fetch("http://localhost:8000/api/zim/search/" + searching)
        console.log(res)
        res.then((data) => {
            return data.json()
        }).then((data) => {
            console.log(data)
            setFiles(data)
        })

    };
    return (
        <>
            {buttonSearch && <button onClick={function(){setIsSearch(true); setButtonSearch(false); setIsIframe(false)}} 
            className="btn btn-danger navbar-btn">Search</button>}
            {isIframe && <iframe id="iframe"  title="index" src="http://localhost:9454"></iframe>}
            {isSearch && <div className="container-fluid">
                <span>Total files: {files.length} </span>
                <div className='language-bar'>
                    <div class="topnav">
                        <input type="text" placeholder="Search.." onChange={searched}></input>
                        <button className="btn btn-danger navbar-btn" onClick={getData}>Search</button>
                    </div>
                </div>
            </div>}
            {isSearch && <div className="container">
                <h1>Search Results</h1>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Size</th>
                            <th>Status</th>
                            <th>Download</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files.map((file) => (

                            <tr key={file.id}>
                                <td>{file.name}</td>
                                <td>{file.size}</td>
                                <td>{file.status}</td>
                                <td><a href={file.url = "http://localhost:8000/download/" + file.id}>Download</a></td>
                            </tr>
                        ))}
                    </tbody>
                </table>

            </div>}

        </>
    );
}

export default Search;