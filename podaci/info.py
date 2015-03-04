from podaci import PodaciView

class Home(PodaciView):
	template_name = "podaci/home.jinja"

	def get_context_data(self):
		self.clear_breadcrumbs()
		num_displayed = 40
		tag_cnt, tags = self.fs.list_user_tags(self.request.user, root=False)
		file_cnt, files = self.fs.list_user_files(self.request.user, _size=num_displayed)
		return {
			"num_files_displayed": min(40, file_cnt),
			"num_tags": tag_cnt,
			"num_files": file_cnt,
			"result_tags": tags,
			"result_files": files,
		}


class Help(PodaciView):
	template_name = "podaci/help.jinja"


class Status(PodaciView):
	template_name = "podaci/status.jinja"

	def get_context_data(self):
		pass

class Statistics(PodaciView):
	template_name = "podaci/statistics.jinja"

	def get_context_data(self):
		pass
