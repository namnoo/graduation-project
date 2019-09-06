package com.spring.example;

import java.text.DateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import javax.inject.Inject;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.spring.dto.AddressVO;
import com.spring.dto.MemberVO;
import com.spring.dto.StreetlampVO;
import com.spring.service.MemberService;
import com.spring.service.StreetlampService;

/**
 * Handles requests for the application home page.
 */
@Controller
public class HomeController {
	
	private static final Logger logger = LoggerFactory.getLogger(HomeController.class);
	
	/**
	 * Simply selects the home view to render by returning its name.
	 */
	
	@Autowired
	private MemberService service;
	@Autowired
	private StreetlampService service2;
	
	@RequestMapping(value = "/", method = {RequestMethod.GET, RequestMethod.POST}, produces="text/json;charset=UTF-8")
	public String home(Locale locale, Model model, HttpServletRequest request, AddressVO addressVO) throws Exception{
		logger.info("home");
		
		List<MemberVO> memberList = service.selectMember();
		List<StreetlampVO> memberList2 = service2.selectMember2();
	
		model.addAttribute("memberList",memberList);
		model.addAttribute("memberList2",memberList2);
		
		addressVO.setAddress(request.getParameter("address"));
		
		return "home";
	}
	
}
