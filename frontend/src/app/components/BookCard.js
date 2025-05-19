export default function BookCard({ book }) {
  const imageUrl = `https://covers.openlibrary.org/b/isbn/${book.Book_ID}-M.jpg`;

  return (
    <div className="border border-gray-200 rounded-lg p-4 w-[200px] text-center shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1">
      <img 
        src={imageUrl} 
        alt={book.Book_Title} 
        width={100} 
        height={150}
        className="object-cover rounded-md mb-2 mx-auto"
      />
      <h3 className="text-base font-medium h-[2.4em] overflow-hidden line-clamp-2">
        {book.Book_Title}
      </h3>
      <p className="text-gray-600 font-bold mt-2">
        Score: {book.Recommendation_Score.toFixed(2)}
      </p>
    </div>
  );
} 