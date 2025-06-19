// mushi-frontend/src/components/cart/Cart.jsx
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faClosedCaptioning,
  faMicrophone,
} from "@fortawesome/free-solid-svg-icons";
import { useLanguage } from "@/context/LanguageContext";
import "./Cart.css";
import { Link, useNavigate } from "react-router-dom";

function Cart({ data, cardRefs = { current: {} }, onMouseEnter, onMouseLeave }) {
  const { language } = useLanguage();
  const navigate = useNavigate();

  return (
    <div className="flex flex-col w-full space-y-7">
      <div className="w-full space-y-4 flex flex-col">
        {data &&
          data.slice(0, 7).map((item) => (
            <div
              key={item.id}
              style={{ borderBottom: "1px solid rgba(255, 255, 255, .075)" }}
              className="flex pb-4 items-center group"
              ref={(el) => { if (cardRefs.current) cardRefs.current[item.id] = el; }}
              onMouseEnter={() => onMouseEnter && onMouseEnter(item.id, cardRefs.current[item.id])}
              onMouseLeave={() => onMouseLeave && onMouseLeave()}
            >
              <img
                src={`https://wsrv.nl/?url=${item.poster_url || item.poster}`}
                alt={item.title}
                className="flex-shrink-0 w-[60px] h-[75px] rounded-md object-cover cursor-pointer"
                onClick={() => navigate(`/anime/details/${item.id}`)}
              />
              <div className="flex flex-col ml-4 space-y-2 w-full">
                <Link
                  to={`/anime/details/${item.id}`}
                  className="w-full line-clamp-2 text-white text-[1em] font-[500] hover:cursor-pointer hover:text-[#ffbade] transform transition-all ease-out max-[1200px]:text-[14px]"
                >
                  {language === "EN" ? item.title : (item.jname || item.japanese_title)}
                </Link>
                <div className="flex items-center flex-wrap w-fit space-x-1">
                  {item.tvInfo?.sub && (
                    <div className="flex space-x-1 justify-center items-center bg-[#B0E3AF] rounded-[4px] px-[4px] text-black py-[2px]">
                      <FontAwesomeIcon
                        icon={faClosedCaptioning}
                        className="text-[12px]"
                      />
                      <p className="text-[12px] font-bold">{item.tvInfo.sub}</p>
                    </div>
                  )}
                  {item.tvInfo?.dub && (
                    <div className="flex space-x-1 justify-center items-center bg-[#B9E7FF] rounded-[4px] px-[8px] text-black py-[2px]">
                      <FontAwesomeIcon
                        icon={faMicrophone}
                        className="text-[12px]"
                      />
                      <p className="text-[12px] font-bold">{item.tvInfo.dub}</p>
                    </div>
                  )}
                  <div className="flex items-center w-fit pl-1 gap-x-1">
                    <div className="dot"></div>
                    <p className="text-[14px] text-[#D2D2D3]">
                      {item.tvInfo?.showType || item.show_type}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}

export default Cart;
