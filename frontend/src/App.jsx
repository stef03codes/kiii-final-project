import { useState } from 'react'
import { useEffect } from 'react'

function App() {
  
  const [formData, setFormData] = useState({
    title: "",
    author: "",
    isbn: ""
  })
  const [books, setBooks] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/books")
      .then((res) => res.json())
      .then((data) => setBooks(data))
      .catch(console.error);
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:8000/books/add", {
        method: "POST",
        headers: { "Content-type": "application/json" },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setBooks((prev) => [...prev, data])
    } catch (error) {
      console.log(error);
    }
  }

  const handleDelete = async (e) => {
    try {
      await fetch("http://localhost:8000/books/delete/" + e.target.id, { method: "DELETE" });
      setBooks((prev) => prev.filter(book => book.id !== e.target.id));
    } catch (error) {
      console.log(error)
    }
  }

  return (
    <div className="w-75 mx-auto">
      <div className="card p-3 mt-3 bg-light">
        <h1 className="text-center">Books App</h1>
      </div>
      <div className="card p-3 mt-3 bg-light">
        <form onSubmit={handleSubmit}>
          <div>
            <label className="form-label">Title</label>
            <input type="text" name='title' className="form-control" onChange={handleChange} />
          </div>
          <div className="mt-3">
            <label className="form-label">Author</label>
            <input type="text" name='author' className="form-control" onChange={handleChange} />
          </div>
          <div className="mt-3">
            <label className="form-label">ISBN</label>
            <input type="text" name='isbn' className="form-control" onChange={handleChange} />
          </div>
          <div className="mt-3">
            <button type="submit" className="btn btn-primary me-2">Save Book</button>
            <button type="reset" className="btn btn-secondary">Clear fields</button>
          </div>
        </form>
      </div>
      <div className="card p-3 mt-3 bg-light">
        <table className="table table-bordered">
          <thead className='rounded'>
            <tr>
              <th>Title</th>
              <th>Author</th>
              <th>ISBN</th>
              <th>Manage</th>
            </tr>
          </thead>
          <tbody>
            {books.map((book, index) => (
              <tr key={index}>
                <td>{book.title}</td>
                <td>{book.author}</td>
                <td>{book.isbn}</td>
                <td>
                  <button 
                    type='button' 
                    className='btn btn-danger' 
                    id={book.id} 
                    onClick={handleDelete}
                  >Delete Book</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default App
